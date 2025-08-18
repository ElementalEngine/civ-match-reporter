import os
import pytest
from app.parsers import civ7

def _test_parse_civ7_save(file_path, expected_game, expected_turn, expected_mode, expected_map_type, expected_players):
    # Path to a test Civ7 save file
    test_save_path = os.path.join(os.path.dirname(__file__), file_path)
    assert os.path.exists(test_save_path), f"Save file not found: {test_save_path}"

    with open(test_save_path, 'rb') as f:
        buffer = f.read()
    # Parse the save file
    result = civ7.parse_civ7_save(buffer)

    # Assert the result is a dict and contains expected keys (customize as needed)
    assert isinstance(result, dict)
    assert 'players' in result
    assert result['game'] == expected_game
    assert result['turn'] == expected_turn
    assert result['game_mode'] == expected_mode
    assert result['map_type'] == expected_map_type

    assert len(result['players']) == len(expected_players)
    for i, expected in enumerate(expected_players):
        player = result['players'][i]
        assert player['steam_id'] == expected['steam_id']
        assert player['user_name'] == expected['user_name']
        assert player['civ'] == expected['civ']
        assert player.get('leader', None) == expected.get('leader', None)
        assert player['team'] == expected['team']

def test_parse_civ7_save_3v3_T10():
    expected_players = [
        { 
            'steam_id': -1,
            'user_name': '',
            'civ': 'CIVILIZATION_ROME',
            'leader': 'LEADER_FRIEDRICH',
            'team': 0
        },
        {
            'steam_id': -1,
            'user_name': '',
            'civ': 'CIVILIZATION_MISSISSIPPIAN',
            'leader': 'LEADER_HIMIKO',
            'team': 0
        },
        {
            'steam_id': '76561198021954438',
            'user_name': '-KC- CanuckSoldier[CPL]',
            'civ': 'CIVILIZATION_GREECE',
            'leader': 'LEADER_MACHIAVELLI',
            'team': 0
        },
        {
            'steam_id': -1,
            'user_name': '',
            'civ': 'CIVILIZATION_EGYPT',
            'leader': 'LEADER_NAPOLEON_ALT',
            'team': 1
        },
        {
            'steam_id': -1,
            'user_name': '',
            'civ': 'CIVILIZATION_CARTHAGE',
            'leader': 'LEADER_AUGUSTUS',
            'team': 1
        },
        {
            'steam_id': -1,
            'user_name': '',
            'civ': 'CIVILIZATION_PERSIA',
            'leader': 'LEADER_GENGHIS_KHAN',
            'team': 1
        }
    ]
    _test_parse_civ7_save(
        file_path='../data/civ7TestSaves/3v3_T10.Civ7Save',
        expected_game='civ7',
        expected_turn=10,
        expected_mode='team',
        expected_map_type='Continents Plus',
        expected_players=expected_players
    )
    
def test_parse_civ7_save_5player_ffa():
    expected_players = [
        {
            'steam_id': '76561198046790489',
            'user_name': 'Arjou',
            'civ': 'CIVILIZATION_MISSISSIPPIAN',
            'leader': 'LEADER_FRIEDRICH',
            'team': 0
        },
        {
            'steam_id': '76561198062006970',
            'user_name': 'snyperanihilatr1',
            'civ': 'CIVILIZATION_ROME',
            'leader': 'LEADER_IBN_BATTUTA',
            'team': 1
        },
        {
            'steam_id': '76561198271354842',
            'user_name': 'Unknown',
            'civ': 'CIVILIZATION_MAYA',
            'leader': 'LEADER_CHARLEMAGNE',
            'team': 2
        },
        {
            'steam_id': '76561198027853694',
            'user_name': 'Underbow',
            'civ': 'CIVILIZATION_AKSUM',
            'leader': 'LEADER_XERXES_ALT',
            'team': 3
        },
        {
            'steam_id': '76561198114596168',
            'user_name': 'PineapplePizzaPriest',
            'civ': 'CIVILIZATION_PERSIA',
            'leader': 'LEADER_ISABELLA',
            'team': 4
        }
    ]
    _test_parse_civ7_save(
        file_path='../data/civ7TestSaves/5playerFFA.Civ7Save',
        expected_game='civ7',
        expected_turn=18,
        expected_mode='ffa',
        expected_map_type='Continents',
        expected_players=expected_players
    )

def test_parse_civ7_save_duel():
    expected_players = [
        {
            'steam_id': '76561198330293027',
            'user_name': 'Calcifer',
            'civ': 'CIVILIZATION_GREECE',
            'leader': 'LEADER_MACHIAVELLI',
            'team': 0
        },
        {
            'steam_id': -1,
            'user_name': '',
            'civ': 'CIVILIZATION_MAURYA',
            'leader': 'LEADER_ASHOKA',
            'team': 1
        }
    ]
    _test_parse_civ7_save(
        file_path='../data/civ7TestSaves/duel.Civ7Save',
        expected_game='civ7',
        expected_turn=1,
        expected_mode='duel',
        expected_map_type='Archipelago',
        expected_players=expected_players
    )