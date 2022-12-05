from .chacha20generator import ChaChaRand
from .helpers import sha3_256_user_id, format_friend
from sqlite3 import connect
import requests

CHACHA = None

# Using a randomness beacon allows further verification of the randomness
def get_seed():
    """
    Does a GET request to a randomness beacon API to get the last pulse as seed.
    :return: A 512-bit random string that can be used as seed by a pseudo random generator.
    """
    response = requests.get('https://random.uchile.cl/beacon/2.0-beta1/pulse/last')
    return response.json()['pulse']['outputValue']

def shuffle(users: list, first_call=False):
    global CHACHA
    if first_call:
        CHACHA = ChaChaRand(get_seed())
    return CHACHA.shuffle(users)

def shuffle_players(ids_players: list, database: str, token: str):
    shuffled_players = shuffle(ids_players, first_call=True)
    con = connect(database)
    cur = con.cursor()
    for i in range(len(shuffled_players)):
        # Hiding secret friend
        gives = sha3_256_user_id(shuffled_players[i])
        receives = shuffled_players[(i + 1) % len(shuffled_players)]
        cur.execute(f"INSERT INTO secret_santa VALUES('{gives}', {receives})")
        msg = (
            "Woof! Vengo a anunciarte los resultados:\n\n"+
            format_friend(database, receives)+
            "\n\n"+
            "Info Adicional: Los resultados se encuentran hasheados en la BD por lo que nadie excepto tú conocerá el resultado ;)\n"
        )
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={shuffled_players[i]}&text={msg}")
        print(f"Sent to {shuffled_players[i]}")
    con.commit()
    con.close()