from .chacha20generator import ChaChaRand
from .helpers import sha3_256_user_id
import requests

# Using a randomness beacon allows further verification of the randomness
def get_seed():
    """
    Does a GET request to a randomness beacon API to get the last pulse as seed.
    :return: A 512-bit random string that can be used as seed by a pseudo random generator.
    """
    response = requests.get('https://random.uchile.cl/beacon/2.0-beta1/pulse/last')
    return response.json()['pulse']['outputValue']

def shuffle(users: list):
    random = ChaChaRand(get_seed())
    return random.shuffle(users)

def shuffle_players(ids_players: list, database: str):
    shuffled_players = shuffle(ids_players)

    con = connect(database)
    cur = con.cursor()
    for i in len(shuffled_players):
        # Hiding secret friend
        gives = sha3_256_user_id(shuffled_players[i])
        receives = shuffled_players[(i + 1) % len(shuffled_players)]
        cur.execute(f"INSERT INTO secret_santa VALUES({gives}, {receives})")
    con.commit()
    con.close()