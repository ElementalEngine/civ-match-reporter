import os
import pytest
from app.parsers import civ7

def test_parse_civ7_save():
    # Path to a test Civ7 save file
    test_save_path = os.path.join(os.path.dirname(__file__), '../data/civ7TestSaves/3v3_T10.Civ7Save')
    assert os.path.exists(test_save_path), f"Save file not found: {test_save_path}"

    with open(test_save_path, 'rb') as f:
        buffer = f.read()
    # Parse the save file
    result = civ7.parse_civ7_save(buffer)

    # Assert the result is a dict and contains expected keys (customize as needed)
    assert isinstance(result, dict)
    assert 'players' in result
    assert result['game'] == 'civ7'
    assert result['turn'] == 10
    assert result['game_mode'] == 'team'
    assert result['map_type'] == 'Continents Plus'

    expected_players = [
        {'steam_id': -1, 'user_name': '', 'civ': 'CIVILIZATION_ROME', 'leader': 'LEADER_FRIEDRICH', 'team': 0},
        {'steam_id': -1, 'user_name': '', 'civ': 'CIVILIZATION_MISSISSIPPIAN', 'leader': 'LEADER_HIMIKO', 'team': 0},
        {'steam_id': '76561198021954438', 'user_name': '-KC- CanuckSoldier[CPL]', 'civ': 'CIVILIZATION_GREECE', 'leader': 'LEADER_MACHIAVELLI', 'team': 0},
        {'steam_id': -1, 'user_name': '', 'civ': 'CIVILIZATION_EGYPT', 'leader': 'LEADER_NAPOLEON_ALT', 'team': 1},
        {'steam_id': -1, 'user_name': '', 'civ': 'CIVILIZATION_CARTHAGE', 'leader': 'LEADER_AUGUSTUS', 'team': 1},
        {'steam_id': -1, 'user_name': '', 'civ': 'CIVILIZATION_PERSIA', 'leader': 'LEADER_GENGHIS_KHAN', 'team': 1},
    ]
    assert len(result['players']) == len(expected_players)
    for i, expected in enumerate(expected_players):
        player = result['players'][i]
        assert player['steam_id'] == expected['steam_id']
        assert player['user_name'] == expected['user_name']
        assert player['civ'] == expected['civ']
        assert player.get('leader', None) == expected.get('leader', None)
        assert player['team'] == expected['team']
