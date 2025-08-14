import os
import pytest
from app.parsers import civ6

def test_parse_civ6_save():
    # Path to a test Civ6 save file
    test_save_path = os.path.join(os.path.dirname(__file__), '../data/testSaves/test.Civ6Save')
    assert os.path.exists(test_save_path), f"Save file not found: {test_save_path}"

    with open(test_save_path, 'rb') as f:
        buffer = f.read()
    # Parse the save file
    result = civ6.parse_civ6_save(buffer)

    # Assert the result is a dict and contains expected keys (customize as needed)
    assert isinstance(result, dict)
    assert 'players' in result
    assert result['game'] == 'civ6'
    assert result['turn'] == 108
    assert result['game_mode'] == 'ffa'
    assert result['map_type'] == 'Lakes'

    expected_players = [
        {'steam_id': 'CEO of Spearfighting', 'user_name': 'CEO of Spearfighting', 'civ': 'LEADER_RAMSES', 'team': 0, 'player_alive': True},
        {'steam_id': -1, 'user_name': '', 'civ': 'LEADER_HOJO', 'team': 1, 'player_alive': True},
        {'steam_id': -1, 'user_name': '', 'civ': 'LEADER_LADY_TRIEU', 'team': 2, 'player_alive': False},
        {'steam_id': -1, 'user_name': '', 'civ': 'LEADER_SALADIN', 'team': 3, 'player_alive': True},
        {'steam_id': -1, 'user_name': '', 'civ': 'LEADER_TRAJAN', 'team': 4, 'player_alive': False},
        {'steam_id': -1, 'user_name': '', 'civ': 'LEADER_JAYAVARMAN', 'team': 5, 'player_alive': False},
        {'steam_id': -1, 'user_name': '', 'civ': 'LEADER_TAMAR', 'team': 6, 'player_alive': False},
        {'steam_id': -1, 'user_name': '', 'civ': 'LEADER_PHILIP_II', 'team': 7, 'player_alive': True},
    ]
    assert len(result['players']) == len(expected_players)
    for i, expected in enumerate(expected_players):
        player = result['players'][i]
        assert player['steam_id'] == expected['steam_id']
        assert player['user_name'] == expected['user_name']
        assert player['civ'] == expected['civ']
        assert player['team'] == expected['team']
        assert player['player_alive'] == expected['player_alive']
