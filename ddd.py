from typing import Optional
import dropbox
import sys
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

ACCESS_TOKEN = "sl.B8XbSn3ocOXC7vFS1P6r8FdAvdPcp-zG-bH5UOlEpQKLBkoJOI7H4oxYy8lc28dOmdtI0LclT9CqH3pmj0sDsUjkTxMCq7qvEbLa0IcKgOsHnacS6l9XG4LX6fZq--sYtl71qgXRbpQT"
LOCALFILE = 'text.txt'

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/get_file')
async def get_file(file: UploadFile):
    print(file.filename)
    return {"filename": file}

@app.post("/upload_file/")
async def upload_file(
):
    with dropbox.Dropbox(ACCESS_TOKEN) as dbx:

        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
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
