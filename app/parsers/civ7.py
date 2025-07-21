def parse_civ7_save(file_bytes: bytes, version: str):
    return {
        "game": "civ7",
        "turn": 42,
        "cloud_game": False,
        "players": [
            {"steam_id": "p3", "civ": "Egypt", "team": 1},
            {"steam_id": "p4", "civ": "France", "team": 2}
        ],
        "game_mode": "ffa",
        "parser_version": version
    }
