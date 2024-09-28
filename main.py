import dropbox
import sys
import pathlib
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from tools import set_to_cache, get_link
import os
from dotenv import load_dotenv
from celery_worker import delayed_delete

load_dotenv(override=True)


ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
app = FastAPI()

templates = Jinja2Templates(directory="templates")



@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/upload_file/")
async def upload_file(file: UploadFile, password: str =  Form(...), expiration_time: int = Form(...)
):
    with dropbox.Dropbox(ACCESS_TOKEN) as dbx:

        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
            folder = pathlib.Path(".") 
            LOCALFILE= file.filename
            filepath = folder / LOCALFILE
            target = "/Temp/" 
            targetfile = target + LOCALFILE 

        except AuthError:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web.")
    with filepath.open("rb") as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        print("Uploading " + LOCALFILE)
        try:
            meta = dbx.files_upload(
                f.read(), targetfile, mode=dropbox.files.WriteMode("overwrite"))
            link = dbx.sharing_create_shared_link(targetfile)
            url = link.url
            url_dl = url[:-1] + "1"
            task = delayed_delete.apply_async(args=(LOCALFILE,), countdown= expiration_time * 3600)

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


@app.post("/download_file/")
async def download_file(password: str =  Form(...), hash: str = Form(...)):
    with dropbox.Dropbox(ACCESS_TOKEN) as dbx:
        try:
            dbx.users_get_current_account()
            downloading= get_link(password, hash)
        except AuthError:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web.")

    return JSONResponse(content={"link": downloading})

