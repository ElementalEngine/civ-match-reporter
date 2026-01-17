from app.parsers.civ6leaders import civ6_leaders_dict
from app.parsers.civ7leaders import civ7_leaders_dict

def get_cpl_name(game: str, civ: str, leader: str = None) -> str:
    """
    Convert in-game civilization and leader names to CPL standard names.

    Args:
        game (str): The game identifier, either "civ6" or "civ7".
        civ (str): The in-game civilization name.
        leader (str, optional): The in-game leader name. Required for Civ7.

    Returns:
        str: The CPL standard civilization name.
    """
    if game == "civ6":
        return civ6_leaders_dict.get(civ, civ)
    elif game == "civ7":
        if leader is None:
            raise ValueError("Leader name must be provided for Civ7.")
        return civ7_leaders_dict.get((civ, leader), civ)
    else:
        raise ValueError("Unsupported game type. Use 'civ6' or 'civ7'.")