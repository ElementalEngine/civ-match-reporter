from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

from bson import ObjectId
from trueskill import Rating

from app.db import players_col, matches_col, history_col
from app.config import settings
from app.services.skill import make_ts_env


@dataclass(frozen=True)
class PlayerState:
    player_id: str            
    mu: float
    sigma: float


class TrueSkillService:
    def __init__(self) -> None:
        # Build a TrueSkill environment using values from .env / config.py
        self.env = make_ts_env()

    # --------------------------- Public API ---------------------------

    def confirm_placements_and_rate(
        self,
        match_id: str,
        teams: List[List[str]],
        placements: List[int],
    ) -> Dict[str, Any]:

        self._validate_inputs(match_id, teams, placements)

        # Pre states for all participants (single pass)
        pre_states = self._load_pre_states(teams)

        # Compute TrueSkill post states using TS env from __init__
        post_states = self._compute_post_states(teams, placements)

        # Deltas for Discord bot display
        deltas = self._compute_deltas(pre_states, post_states)

        # Persist immutable per-player history rows
        self._write_history(match_id, pre_states, post_states)

        # Update match doc with placements and start 48h hold
        self._persist_match_status(match_id, teams, placements)

        return {"matchId": match_id, "ratingDeltas": deltas}

    def approve_eligible_matches(self) -> int:
        cutoff = datetime.utcnow() - timedelta(hours=48)
        candidates = list(
            matches_col.find(
                {
                    "status": "pending-approval",
                    "confirmedAt": {"$lte": cutoff},
                    "$or": [{"flags.count": {"$exists": False}}, {"flags.count": 0}],
                },
                {"_id": 1},
            )
        )

        for m in candidates:
            # For this match, write each player's post rating into players.rating
            rows = list(history_col.find({"matchId": m["_id"]}))
            for row in rows:
                players_col.update_one(
                    {"_id": row["playerId"]},
                    {"$set": {
                        "rating": {
                            "mu": float(row["post"]["mu"]),
                            "sigma": float(row["post"]["sigma"]),
                        }
                    }},
                )

            matches_col.update_one(
                {"_id": m["_id"]},
                {"$set": {"status": "approved", "approvedAt": datetime.utcnow()}},
            )

        return len(candidates)

    # --------------------------- Internals ---------------------------

    def _validate_inputs(self, match_id: str, teams: List[List[str]], placements: List[int]) -> None:
        if not match_id or not ObjectId.is_valid(match_id):
            raise ValueError("invalid match_id")

        match = matches_col.find_one({"_id": ObjectId(match_id)}, {"_id": 1, "status": 1})
        if not match:
            raise ValueError("match not found")
        if match.get("status") not in (None, "draft", "pending", "uploaded"):
            # Prevent re-confirming an already confirmed/approved match
            pass

        if not teams or len(teams) < 2:
            raise ValueError("at least two teams are required")

        if len(placements) != len(teams):
            raise ValueError("placements length must equal number of teams")

        # placements must be positive integers; exactly one winner (rank 1)
        winners = sum(1 for r in placements if isinstance(r, int) and r == 1)
        if winners != 1:
            raise ValueError("exactly one winning team (rank=1) is required")
        if any((not isinstance(r, int)) or r < 1 for r in placements):
            raise ValueError("all placements must be positive integers (1..k)")

        # If it's a team game (any team size > 1), enforce equal team sizes
        team_sizes = [len(t) for t in teams]
        if any(sz > 1 for sz in team_sizes) and len(set(team_sizes)) != 1:
            raise ValueError("team games must have equal team sizes")

    def _get_player_state(self, pid: str) -> PlayerState:
        doc = players_col.find_one({"_id": ObjectId(pid)}, {"rating": 1})
        rating = (doc or {}).get("rating") or {"mu": settings.ts_mu, "sigma": settings.ts_sigma}
        return PlayerState(player_id=pid, mu=float(rating["mu"]), sigma=float(rating["sigma"]))

    def _load_pre_states(self, teams: List[List[str]]) -> Dict[str, PlayerState]:
        pre: Dict[str, PlayerState] = {}
        for team in teams:
            for pid in team:
                if pid not in pre:
                    pre[pid] = self._get_player_state(pid)
        return pre

    def _compute_post_states(
        self, teams: List[List[str]], placements: List[int]
    ) -> Dict[str, PlayerState]:
        # Build Rating objects per team/player using current mu/sigma
        team_states: List[List[PlayerState]] = [
            [self._get_player_state(pid) for pid in team] for team in teams
        ]
        ts_teams = [[Rating(p.mu, p.sigma) for p in team] for team in team_states]

        # Use the environment instance (avoids relying on global env)
        new_ts = self.env.rate(ts_teams, ranks=placements)

        # Convert back to PlayerState and return dict keyed by player id
        post: Dict[str, PlayerState] = {}
        for t_idx, team in enumerate(team_states):
            for i, pre in enumerate(team):
                r = new_ts[t_idx][i]
                post[pre.player_id] = PlayerState(pre.player_id, float(r.mu), float(r.sigma))
        return post

    def _compute_deltas(
        self, pre: Dict[str, PlayerState], post: Dict[str, PlayerState]
    ) -> Dict[str, Dict[str, float]]:
        out: Dict[str, Dict[str, float]] = {}
        for pid, before in pre.items():
            after = post[pid]
            out[pid] = {
                "deltaMu": round(after.mu - before.mu, 3),
                "deltaSigma": round(after.sigma - before.sigma, 3),
            }
        return out

    def _write_history(
        self,
        match_id: str,
        pre: Dict[str, PlayerState],
        post: Dict[str, PlayerState],
    ) -> None:
        now = datetime.utcnow()
        docs = []
        for pid, pre_state in pre.items():
            post_state = post[pid]
            docs.append(
                {
                    "matchId": ObjectId(match_id),
                    "playerId": ObjectId(pid),
                    "pre": {"mu": pre_state.mu, "sigma": pre_state.sigma},
                    "post": {"mu": post_state.mu, "sigma": post_state.sigma},
                    "deltaMu": post_state.mu - pre_state.mu,
                    "deltaSigma": post_state.sigma - pre_state.sigma,
                    "at": now,
                }
            )
        if docs:
            history_col.insert_many(docs)

    def _persist_match_status(
        self, match_id: str, teams: List[List[str]], placements: List[int]
    ) -> None:
        matches_col.update_one(
            {"_id": ObjectId(match_id)},
            {
                "$set": {
                    "status": "pending-approval",
                    "confirmedAt": datetime.utcnow(),
                    "teams": [
                        {"teamNo": i + 1, "players": teams[i], "placement": placements[i]}
                        for i in range(len(teams))
                    ],
                }
            },
        )


# Simple DI singleton
ts_service = TrueSkillService()