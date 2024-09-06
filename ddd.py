from typing import Optional
import dropbox
import sys
from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

ACCESS_TOKEN = "sl.B8at-3ELLVuv1PCwzsL2vQikKzKYtqNgGKwoUNAT8FkQmcoOTh8I33P42tzeIaHE1WMJmbJv4H4OJwjQy8T3NxzH_sLdhJOfM3GS5Qyd_eb1ybmx3q5pAtqPkPxqVsicMVYBbxM1rWvA"
LOCALFILE = 'text.txt'

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
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()

    return {"download": "completed"}
