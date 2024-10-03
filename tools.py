"""funcions to work with cache"""
import hashlib
import redis


cache = redis.Redis(host='redis_database', port=6379, decode_responses=True)


def link_to_hash(link: str, password: str):
    """converts link and password to hash
    Args:
        link (str): link from dropbox
        password (str): users password

    Returns:
        str: hash 
    """
    hash_for_downloading= hashlib.sha256(
        (link + password + "asdfghjkQWERTY").encode('utf-8')).hexdigest()
    return hash_for_downloading

def set_to_cache(link: str, expiration_time: int, password: str):
    """creates a key-value pare in cache

    Args:
        link (str): link from dropbox
        expiration_time (int): time in seconds for awaliabitily of the link
        password (str): users password

    Returns:
        str: hash, to return to HTML
    """
    hash_for_downloading = link_to_hash(link, password)
    cache.set(hash_for_downloading, link, expiration_time * 3600)
    return hash_for_downloading

def get_link(password: str, hash_users: str):
    """searches in redis cache for a pair of password - provided hash

    Args:
        password (str): users password
        hash_users (str): users hash

    Returns:
        link, or message why it isnt possible
    """
    output = cache.get(hash_users)
    if output is None:
        return "Your link doesn't exists or expired"
    if hash_users == link_to_hash(output, password):
        return output
    return "wrong password"
