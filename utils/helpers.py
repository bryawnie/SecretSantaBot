import hashlib

# Auxiliary function
def get_new_id(database: str, field_name: str, table_name: str, user_id: int):
    """
    Returns the next id for a new row in a table, given the user_id.
    Specifically designed for likes and dislikes tables.
    """
    con = connect(database)
    last_id = con.cursor().execute(f"SELECT {field_name} FROM {table_name} WHERE user_id={user_id} ORDER BY {field_name} DESC LIMIT 1").fetchone()
    con.close()
    if last_id is None:
        return 1
    return int(last_id[0]) + 1

# Auxiliary function
def get_user_game_id(database: str, user_id: int):
    """
        Returns the game_id of the user.
    """
    con = connect(database)
    game_id = con.cursor().execute(f"SELECT game_id FROM friends WHERE user_id={user_id}").fetchone()[0]
    con.close()
    return game_id

# Auxiliary function
def is_ready(database: str, user_id: int):
    """
        Returns True if user is ready to play, False otherwise.
        Ready means that user has sent the command /ready.
    """
    con = connect(database)
    ready = con.cursor().execute(f"SELECT ready FROM friends WHERE user_id={user_id}").fetchone()[0]
    con.close()
    return ready == 1

# Auxiliary function
def get_players(database: str, game_id: int):
    """
        Returns a list of all the players of a game.
    """
    con = connect(database)
    players = con.cursor().execute(f"SELECT user_id, ready FROM friends WHERE game_id={game_id}").fetchall()
    con.close()
    return players

def sha3_256_user_id(user_id: int):
    """
        Returns the sha3_256 hash of the user_id.
    """
    return hashlib.sha3_256(str(user_id).encode('utf-8')).hexdigest()


def get_secret_friend(database, id_player):
    con = connect(DATABASE)
    cur = con.cursor()
    receives = cur.execute(f"SELECT receives FROM secret_santa WHERE gives='{sha3_256_user_id(id_player)}'").fetchone()
    if receives is None:
        return None
    secret_friend = cur.execute(f"SELECT name FROM friends WHERE user_id={receives[0]}").fetchone()[0]
    return secret_friend