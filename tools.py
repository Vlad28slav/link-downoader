"""funcions to work with cache"""
import string
import random
from typing import Optional
import hashlib
import redis

cache = redis.Redis(host='redis_database', port=6379, decode_responses=True)
PEPER ='qwerty'

def link_to_hash(link: str):
    """converts link and password to hash
    Args:
        link (str): link from dropbox
        password (str): users password

    Returns:
        str: hash 
    """
    hash_string = ''.join(random.choices(string.ascii_letters, k=10))

    hash_for_downloading = hashlib.sha256(
        (link + hash_string).encode('utf-8')).hexdigest()
    return hash_for_downloading

def set_to_cache(link: str, expiration_time: int, password: Optional[str] = None):
    """creates a key-value pare in cache

    Args:
        link (str): link from dropbox
        expiration_time (int): time in seconds for awaliabitily of the link
        password (str): users password

    Returns:
        str: hash, to return to HTML
    """
    if password is not None :
        salt = ''.join(random.choices(string.ascii_letters, k=10))
        password_salt_peper = hashlib.sha256(
        (password + salt + PEPER).encode('utf-8')).hexdigest()
        hash_for_downloading = link_to_hash(link)
        event = {
            'salt': salt,
            'password_salt_peper': password_salt_peper,
            'link': link
            }
        cache.hset(hash_for_downloading, mapping=event)
        cache.hexpire(hash_for_downloading, expiration_time * 3600, "salt", 'password_salt_peper', 'link')
        link_to_download = "http://localhost:8000/download_file/" + hash_for_downloading
        return link_to_download
    hash_for_downloading = link_to_hash(link)
    event = {
        'link': link
        }
    cache.hset(hash_for_downloading, mapping=event)
    cache.hexpire(hash_for_downloading, expiration_time * 3600, 'link')
    link_to_download = "http://localhost:8000/download_file/" + hash_for_downloading
    return link_to_download

def get_link(download_link):
    output = cache.hget(download_link, "link")
    if output is None:
        return "Your link doesn't exists or expired"
    password = cache.hget(download_link, "password_salt_peper")
    print("this is :", password)
    if password is None:
        result = cache.hgetall(download_link)
        return result
    return "pass required"


    