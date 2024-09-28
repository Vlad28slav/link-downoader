import redis
import hashlib


cache = redis.Redis(host='redis_database', port=6379, decode_responses=True)


def link_to_hash(link: str, password: str):
    hash = hashlib.sha256((link + password + "asdfghjkQWERTY").encode('utf-8')).hexdigest()
    return hash

def set_to_cache(link: str, expiration_time: int, password: str):
    hash = link_to_hash(link, password)
    cache.set(hash, link, expiration_time * 3600)
    return hash

def get_link(password: str, hash_users: str):
    output = cache.get(hash_users)
    if output is None:
        return "Your link doesn't exists or expired"
    if hash_users == link_to_hash(output, password):
        return output
    return "wrong password"

