from celery import Celery
from dropbox.exceptions import ApiError
import dropbox
import os
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
    with dropbox.Dropbox(ACCESS_TOKEN) as dbx:
        dbx.files_delete_v2(f'/Temp/{file}')
        return f"{file} was deleted"
