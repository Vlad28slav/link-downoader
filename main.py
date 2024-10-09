"""main application module"""
import sys
import pathlib
import os
from typing import Optional
import dropbox
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from dotenv import load_dotenv
from tools import set_to_cache, get_link
from celery_worker import delayed_delete

load_dotenv(override=True)


ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
app = FastAPI()

templates = Jinja2Templates(directory="templates")



@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    """
    Returns:
        html form
    """
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/upload_file")
async def upload_file(file: UploadFile, password: Optional[str] = Form(None), expiration_time: int = Form(...)
):
    """Args:
        file (UploadFile): file that should be downloaded
        password (str): user's input in HTML form. Defaults to Form(...).
        expiration_time (int): user's input in HTML form.. Defaults to Form(...).

    Returns:
        Json object, second element is code for downloading file to user
    """
    with dropbox.Dropbox(ACCESS_TOKEN) as dbx:

        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
            folder = pathlib.Path(".")
            localfile= file.filename
            filepath = folder / localfile
            target = "/Temp/"
            targetfile = target + localfile

        except AuthError:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web.")
    with filepath.open("rb") as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        print("Uploading " + localfile)
        try:
            meta = dbx.files_upload(
                f.read(), targetfile, mode=dropbox.files.WriteMode("overwrite"))
            link = dbx.sharing_create_shared_link(targetfile)
            url = link.url
            url_dl = url[:-1] + "1"
            task = delayed_delete.apply_async(args=(localfile,), countdown= expiration_time * 3600)

        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (err.error.is_path() and
                    err.error.get_path().reason.is_insufficient_space()):
                sys.exit("ERROR: Cannot dowload; insufficient space.")
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()

    code = set_to_cache(url_dl, expiration_time, password)

    return {"you can download your file by your password and this code:" : code}


@app.get("/download_file/{download_link}")
async def download_file(request: Request, download_link):
    result = get_link(download_link)
    if result == "Your link doesn't exists or expired":
        return result
    if result == "pass required":
        return templates.TemplateResponse("password_input.html", {"request": request})

    return {"here's your return pal": result }
