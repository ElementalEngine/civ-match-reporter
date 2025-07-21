from trueskill import Rating, rate
from typing import Dict, List

player_ratings: Dict[str, Rating] = {}

def ensure_ratings(player_ids: List[str]):
    for pid in player_ids:
        if pid not in player_ratings:
            player_ratings[pid] = Rating()

def rate_match(placements: List[List[str]]) -> Dict[str, float]:
    ensure_ratings([pid for team in placements for pid in team])
    teams = [[player_ratings[pid] for pid in team] for team in placements]
    rated = rate(teams)
    delta = {}
    for team, new_team in zip(placements, rated):
        for pid, r in zip(team, new_team):
            delta[pid] = r.mu - player_ratings[pid].mu
            player_ratings[pid] = r
    return delta
