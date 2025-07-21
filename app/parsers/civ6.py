import zlib
from xml.etree import ElementTree
from app.config import CIV_SAVE_PARSER_VERSION

def try_decompress(file_bytes: bytes) -> bytes:
    try:
        return zlib.decompress(file_bytes)
    except zlib.error:
        return file_bytes

def extract_embedded_xml(file_data: bytes) -> ElementTree.Element:
    start = file_data.find(b'<?xml')
    end = file_data.rfind(b'</GameSave>') + len(b'</GameSave>')
    if start == -1 or end == -1:
        raise ValueError("Embedded XML not found in save file")
    xml_bytes = file_data[start:end]
    return ElementTree.fromstring(xml_bytes)

def determine_game_mode(players):
    teams = [p['team'] for p in players]
    unique_teams = set(teams)
    if len(players) == 2:
        return "duel"
    if len(unique_teams) == len(players):
        return "ffa"
    return "team"

def extract_player_info(xml_root):
    players = []
    for p in xml_root.findall(".//Player"):
        civ = p.findtext("Civilization", default="Unknown")
        team = int(p.findtext("Team", default="0"))
        steam_id = p.findtext("SteamID", default="unknown")
        players.append({"steam_id": steam_id, "civ": civ, "team": team})
    return players

def extract_turn(xml_root):
    return int(xml_root.findtext(".//Turn", default="0"))

def extract_cloud_game(xml_root):
    return "Hotseat" in xml_root.findtext("Mode", default="")

def parse_civ6_save(file_bytes: bytes, version: str = CIV_SAVE_PARSER_VERSION):
    decompressed = try_decompress(file_bytes)
    root = extract_embedded_xml(decompressed)

    players = extract_player_info(root)
    turn = extract_turn(root)
    cloud_game = extract_cloud_game(root)

    return {
        "game": "civ6",
        "turn": turn,
        "cloud_game": cloud_game,
        "players": players,
        "game_mode": determine_game_mode(players),
        "parser_version": version
    }