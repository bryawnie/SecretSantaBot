import hashlib
from sqlite3 import connect

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
    con = connect(database)
    cur = con.cursor()
    receives = cur.execute(f"SELECT receives FROM secret_santa WHERE gives='{sha3_256_user_id(id_player)}'").fetchone()
    if receives is None:
        return None
    return receives[0]

def get_name(database, id_player):
    """
        Returns the name of the player.
    """
    con = connect(database)
    name = con.cursor().execute(f"SELECT name FROM friends WHERE user_id={id_player}").fetchone()
    con.close()
    if name is None:
        return None
    return name[0].replace("None", "").strip()

def format_preferences(preferences):
    """
        Returns a string with the likes of a player.
    """
    return '\n'.join([f"{pref[1]}: {pref[2]}" for pref in preferences])

def get_preferences(database, table, id_player):
    """
        Returns a list of all the likes of a player.
    """
    con = connect(database)
    likes = con.cursor().execute(f"SELECT * FROM {table} WHERE user_id={id_player}").fetchall()
    con.close()
    if likes is None:
        return []
    return likes

def format_friend(database, id_friend):
    """
        Returns a string with the name of the player and his secret friend.
    """
    try:
        name = get_name(database, id_friend)
        likes = format_preferences(get_preferences(database, 'likes', id_friend))
        dislikes = format_preferences(get_preferences(database, 'dislikes', id_friend))
        message = (
            f"Tu amix secretx es {name} :D.\n"+
            f"Te daremos algunos datitos para que puedas conocerlx mejor :3.\n"+
            f"Estas son las sugerencias que indicó:\n"+
            f"{likes}\n"+
            f"Y... estas son las cosas que NO le gustan:\n"+
            f"{dislikes}\n"+
            f"Te recuerdo que los montos acordados son regalos entre 5k y 10k ;)\n"+
            f"Espero que te diviertas con tu amix secretx ♥️."
        )
        return message
    except:
        return "Hubo un error al obtener los datos de tu amix secretx :c, pls informale a @bryawnie"
