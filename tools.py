"""funcions to work with cache and a router to handle password-case files"""
import string
import random
from typing import Optional
import hashlib
import redis
from bs4 import BeautifulSoup
from fastapi import APIRouter, Form, status
from fastapi.responses import RedirectResponse


cache = redis.Redis(host='redis_database', port=6379, decode_responses=True)
PEPER ='qwerty'
router = APIRouter()


@router.post("/validate_password")
async def validate_password(download_link: str = Form(...), password: str = Form(...)):
    """Validates password by compairing it with the existing in database

    Args:
        download_link (str): hidden field, always default, given by link 
        password (str): user's input from a template

    Returns:
        starts downloading or asks to re-enter password
    """
    salt = cache.hget(download_link, "salt")
    password_salt_peper_user = hashlib.sha256(
        (password + salt + PEPER).encode('utf-8')).hexdigest()
    password_salt_peper_db = cache.hget(download_link, "password_salt_peper")
    if password_salt_peper_user == password_salt_peper_db:
        output = cache.hget(download_link, "link")
        print(output)
        return RedirectResponse(url= output, status_code=status.HTTP_303_SEE_OTHER)


    return {"your password is not correct":"try again"}



def link_to_hash(link: str):
    """converts link and password to hash for security reasons
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
        cache.hexpire(
            hash_for_downloading, expiration_time * 3600, "salt", 'password_salt_peper', 'link'
            )
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

def get_link(download_link: str):
    """Finds in cache link for downloading or redirects to input page

    Args:
        download_link (str): hash genegated by set_to_cash function

    Returns:
        link for downloading from dropbox or redirection for passworrd input
    """
    output = cache.hget(download_link, "link")
    if output is None:
        return "Your link doesn't exists or expired"
    password_salt_peper = cache.hget(download_link, "password_salt_peper")
    if password_salt_peper is None:
        result = cache.hgetall(download_link)
        return result
    with open('templates/password_input.html', 'r', encoding='utf-8') as file:
        html = file.read()
    soup = BeautifulSoup(html, 'html.parser')
    input_tag = soup.find('input', {'name': 'download_link'})
    input_tag['value'] = download_link
    with open('templates/password_input.html', 'w', encoding='utf-8') as file:
        file.write(soup.prettify())
    return "pass required"
