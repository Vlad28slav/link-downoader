import dropbox
import sys
from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import os
from dotenv import load_dotenv

load_dotenv()

LOCALFILE = 'text.txt'

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/upload_file/")
async def upload_file(file: UploadFile
):
    with dropbox.Dropbox(ACCESS_TOKEN) as dbx:

        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
            LOCALFILE= file.filename
        except AuthError:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web.")
    with open(LOCALFILE, 'rb') as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        print("Uploading " + LOCALFILE)
        try:
            dbx.files_upload(f.read(), "/" + LOCALFILE, mode=WriteMode('overwrite'))
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

    return {"download": "completed"}
