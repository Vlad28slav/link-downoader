"""main application module"""
import sys
import os
import shutil
from typing import Optional
import dropbox
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from dotenv import load_dotenv
from tools import set_to_cache, get_link
from tools import router as validation_router
from celery_worker import delayed_delete

load_dotenv(override=True)


ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
app = FastAPI()
app.include_router(validation_router)
templates = Jinja2Templates(directory="templates")



@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    """
    Returns:
        html form
    """
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/upload_file")
async def upload_file(
    file: UploadFile, password: Optional[str] = Form(None), expiration_time: int = Form(...)
    ):
    """Args:
        file (UploadFile): file that should be uploaded
        password (str): user's input in HTML form. Defaults to Form(...).
        expiration_time (int): user's input in HTML form.. Defaults to Form(...).

    Returns:
        information comment and link for downloading file
    """
    with dropbox.Dropbox(ACCESS_TOKEN) as dbx:

        try:
            dbx.users_get_current_account()
            file_location = f"/project_linker/{file.filename}"
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            localfile= file.filename
            target = "/Temp/"
            targetfile = target + localfile

        except AuthError:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web.")
    with open( file_location, "rb") as f:
        print("Uploading " + localfile)
        try:
            meta = dbx.files_upload(
                f.read(), targetfile, mode=dropbox.files.WriteMode("overwrite"))
            link = dbx.sharing_create_shared_link(targetfile)
            url = link.url
            url_dl = url[:-1] + "1"
            task = delayed_delete.apply_async(args=(localfile,), countdown= expiration_time * 3600)

        except ApiError as err:
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
    os.remove(file_location)

    return {"you can download your file by your password(or without) by clicking on this link:" :
             code}


@app.get("/download_file/{download_link}")
async def download_file(request: Request, download_link: str):
    """Tries to download file but if it is protected with password refers to password input

    Args:
        request (Request): request
        download_link (str): hash of downloding file

    Returns:
        Starts downolading or redirection to password-request form
    """
    result = get_link(download_link)
    if result == "Your link doesn't exists or expired":
        return result
    if result == "pass required":
        return templates.TemplateResponse("password_input.html", {"request": request})
    link = result["link"]
    return RedirectResponse(url= link)
