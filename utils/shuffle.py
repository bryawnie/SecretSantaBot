from .chacha20generator import ChaChaRand
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
