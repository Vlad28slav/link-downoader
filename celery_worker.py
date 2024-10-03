"""Celery worker configuration"""
import os
from celery import Celery
import dropbox
from dotenv import load_dotenv

load_dotenv(override=True)

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')


celery_app = Celery(
    'my_fastapi_celery_app',
    broker='redis://redis_database:6379/0',
    backend='redis://redis_database:6379/0'
)

@celery_app.task()
def delayed_delete(file: str):
    """This function deletes a file from dropbox storage,
    but with user's setted delay

    Args:
        file (str): name of file that will be deleted

    Returns:
        JSON: confirmation of deleting
    """
    with dropbox.Dropbox(ACCESS_TOKEN) as dbx:
        dbx.files_delete_v2(f'/Temp/{file}')
        return f"{file} was deleted"
