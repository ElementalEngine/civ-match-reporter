import logging
from collections import defaultdict
from typing import Any, Dict, List
from bson import ObjectId
from bson.int64 import Int64
from app.parsers import parse_civ7_save, parse_civ6_save  # do not modify parser code
from app.config import settings
from app.models.db_models import MatchModel, StatModel, PlayerModel
from trueskill import Rating
from app.services.skill import make_ts_env
import hashlib

logger = logging.getLogger(__name__)

class MatchServiceError(Exception): ...
class InvalidIDError(MatchServiceError): ...
class ParseError(MatchServiceError): ...
class NotFoundError(MatchServiceError): ...

class MatchService:
    def __init__(self, db):
        self.db = db
        self.pending_matches = db["civ_match_reporter"].pending_matches
        self.validated_matches = db["civ_match_reporter"].validated_matches
        self.players = db["players"].players
        self.stats = db["stats2"]

    @staticmethod
    def _to_oid(match_id: str) -> ObjectId:
        try:
            return ObjectId(match_id)
        except Exception:
            raise InvalidIDError("Invalid match ID")

    @staticmethod
    def _parse_save(file_bytes: bytes) -> Dict[str, Any]:
        if file_bytes.startswith(b'CIV6'):
            parser = parse_civ6_save
        elif file_bytes.startswith(b'CIV7'):
            parser = parse_civ7_save
        else:
            raise ParseError(f"Unrecognized save file format. starts with {file_bytes[:4]!r}")
        try:
            data = parser(file_bytes, settings.civ_save_parser_version)
            logger.info(f"✅ 🔍 Parsed as {data.get('game')}")
            return data
        except Exception as e:
            raise ParseError(f"⚠️ Parse attempt failed: {e}")

    async def match_id_to_discord(self, match):
        for player in match.players:
            if player.steam_id and player.steam_id != '-1':
                discord_id = await self.players.find_one({"steam_id": f"{player.steam_id}"})
                if discord_id:
                    player.discord_id = discord_id.get("discord_id")
        return match

    def get_stat_table(self, is_cloud: bool, match_type: str):
        match_table = ("PBC-" if is_cloud else "") + match_type
        return getattr(self.stats, match_table)

    async def get_player_ranking(self, match: MatchModel, discord_id: str) -> StatModel:
        stat_table = self.get_stat_table(match.is_cloud, match.game_mode)
        player = await stat_table.find_one({"_id": Int64(discord_id)})
        if player:
            player['id'] = player.pop('_id')
            return StatModel(**player)
        else:
            return StatModel(
                id=discord_id,
                mu=settings.ts_mu,
                sigma=settings.ts_sigma,
                games=0,
                wins=0,
                first=0,
                subbedIn=0,
                subbedOut=0,
                civs={},
            )

    async def get_players_current_ranking(self, match: MatchModel) -> Dict[PlayerModel, StatModel]:
        players_ranking = {}
        for player in match.players:
            if player.discord_id == None:
                players_ranking[player.steam_id] = StatModel(
                    id="0",
                    mu=settings.ts_mu,
                    sigma=settings.ts_sigma,
                    games=0,
                    wins=0,
                    first=0,
                    subbedIn=0,
                    subbedOut=0,
                )
            else:
                ranking = await self.get_player_ranking(match, player.discord_id)
                players_ranking[player.steam_id] = ranking
        return players_ranking

    async def update_player_stats(self, match: MatchModel) -> MatchModel:
        players_current_ranking = await self.get_players_current_ranking(match)
        teams = defaultdict(list)
        for p in match.players:
            teams[p.team].append(p)
        print('teams: ', teams)
        team_states: List[List[StatModel]] = [
            [players_current_ranking[p.steam_id] for p in teams[team]] for team in teams
        ]
        ts_teams = [[Rating(p.mu, p.sigma) for p in team] for team in team_states]
        print('ts_teams: ', ts_teams)
        placements = [teams[team][0].placement for team in teams]
        print('placements: ', placements)

        ts_env = make_ts_env()
        new_ts = ts_env.rate(ts_teams, ranks=placements)
        print('new_ts: ', new_ts)

        post: Dict[str, StatModel] = {}
        for t_idx, team in enumerate(team_states):
            for i, pre in enumerate(team):
                r = new_ts[t_idx][i]
                post[str(pre.id)] = StatModel(
                    id=pre.id,
                    mu=float(r.mu),
                    sigma=float(r.sigma),
                    games=pre.games + 1,
                    wins=pre.wins + (1 if pre.mu < r.mu else 0),
                    first=pre.first + (1 if placements[t_idx] == 1 else 0),
                    subbedIn=pre.subbedIn,
                    subbedOut=pre.subbedOut,
                    civs=pre.civs,
                )
        print('post: ', post)
        for p in match.players:
            print('p: ', p)
            p_current_ranking = players_current_ranking[p.steam_id]
            p.delta = round(post[p.discord_id].mu - p_current_ranking.mu) if p.discord_id != None else 0
        return match
        # stat_table = self.get_stat_table(match["is_cloud"], match["game_mode"])
        # stat_table.update_many(
        #     {"_id": {"$in": [p._id for p in post.values()]}},
        #     {"$set": {k: v for p in post.values() for k, v in p.dict().items()}},
        #     upsert=True,
        # )

    async def create_from_save(self, file_bytes: bytes, reporter_discord_id: str, is_cloud: bool) -> Dict[str, Any]:
        parsed = self._parse_save(file_bytes)
        m = hashlib.sha256()
        unique_data = ','.join(
            [parsed['game']] + 
            [parsed['map_type']] +
            [p['civ'] + (p['leader'] if 'leader' in p else '') for p in parsed['players']]
        )
        m.update(unique_data.encode('utf-8'))
        save_file_hash = m.hexdigest()
        res = await self.pending_matches.find_one({"save_file_hash": save_file_hash})
        if res:
            match_id = str(res["_id"])
            del res["_id"]
            res["match_id"] = match_id
            res['repeated'] = True
            return res
        parsed['save_file_hash'] = save_file_hash
        parsed['repeated'] = False
        parsed['reporter_discord_id'] = reporter_discord_id
        parsed['is_cloud'] = is_cloud
        match = MatchModel(**parsed)
        match = await self.match_id_to_discord(match)
        match = await self.update_player_stats(match)
        res = await self.pending_matches.insert_one(match.dict())
        return {"match_id": str(res.inserted_id), **match.dict()}

    async def get(self, match_id: str) -> Dict[str, Any]:
        oid = self._to_oid(match_id)
        doc = await self.pending_matches.find_one({"_id": oid})
        if not doc:
            raise NotFoundError("Match not found")
        doc["match_id"] = str(doc.pop("_id"))
        return doc

    async def update(self, match_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        if not update_data:
            raise MatchServiceError("Empty update payload")
        oid = self._to_oid(match_id)
        res = await self.pending_matches.update_one({"_id": oid}, {"$set": update_data})
        if res.matched_count == 0:
            raise NotFoundError("Match not found")
        updated = await self.pending_matches.find_one({"_id": oid})
        updated["match_id"] = str(updated.pop("_id"))
        logger.info(f"✅ 🔄 Updated match {match_id}")
        return updated

    async def change_order(self, match_id: str, new_order: str) -> Dict[str, Any]:
        oid = self._to_oid(match_id)
        res = await self.pending_matches.find_one({"_id": oid})
        if res == None:
            raise NotFoundError("Match not found")
        new_order_list = new_order.split(' ')
        if len(new_order_list) != len(res['players']):
            raise MatchServiceError(f"New order length does not match number of players ({len(res['players'])})")
        new_order_set = set(new_order_list)
        for i in range(1, len(res['players']) + 1):
            if str(i) not in new_order_set:
                raise MatchServiceError(f"New order must contain all player numbers from 1 to {len(res['players'])}")
        for i, player in enumerate(res['players']):
            res["players"][i]["placement"] = int(new_order_list[i])
        match = MatchModel(**res)
        match = await self.update_player_stats(match)
        changes = {}
        for i, player in enumerate(res['players']):
            changes[f"players.{i}.placement"] = int(new_order_list[i])
            changes[f"players.{i}.delta"] = match.players[i].delta
        print('changes: ', changes)
        await self.pending_matches.update_one({"_id": oid}, {"$set": changes})
        logger.info(f"✅ 🔄 Changed player order for match {match_id}")
        updated = await self.pending_matches.find_one({"_id": oid})
        updated["match_id"] = str(updated.pop("_id"))
        return updated

    async def delete_pending_match(self, match_id: str) -> Dict[str, Any]:
        oid = self._to_oid(match_id)
        res = await self.pending_matches.find_one({"_id": oid})
        if res == None:
            raise NotFoundError("Match not found")
        res["match_id"] = str(res.pop("_id"))
        await self.pending_matches.delete_one({"_id": oid})
        logger.info(f"✅ 🔄 Match {match_id} removed")
        return res

    async def trigger_quit(self, match_id: str, quitter_discord_id: str) -> Dict[str, Any]:
        oid = self._to_oid(match_id)
        res = await self.pending_matches.find_one({"_id": oid})
        if res == None:
            raise NotFoundError("Match not found")
        changes = {}
        for i, player in enumerate(res['players']):
            if player.get('discord_id') == quitter_discord_id:
                changes[f"players.{i}.quit"] = False if res['players'][i]['quit'] else True
                break
        await self.pending_matches.update_one({"_id": oid}, {"$set": changes})
        updated = await self.pending_matches.find_one({"_id": oid})
        updated["match_id"] = str(updated.pop("_id"))
        logger.info(f"✅ 🔄 Match {match_id}, player {quitter_discord_id} quit triggered")
        return updated