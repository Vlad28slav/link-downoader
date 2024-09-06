"""
Backs up and restores a settings file to Dropbox.
This is an example app for API v2.
"""

import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from html.parser import HTMLParser
from fastapi import FastAPI 


#ACCESS_TOKEN = "sl.B8Oq7ppEq30EOx9DdSfeOFt7jOMceyVJKhdrqTcoNGU71DpLHv8phsmDX87RTS7h2Vxe8pS7CZAH2ZNlJn2gHCcpxLGVezbcDfvydVu9gg8aWX_vQoNSXWDhZbkMlrbCpyWS0gyGwuWn"

LOCALFILE = 'text.txt'

# Uploads contents of LOCALFILE to Dropbox
def download_file():
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


class ImageParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for attr, val in attrs:
            if attr == "src" and tag == "img":
                print(f"Found Image: {val!r}")

with open("index.html", mode="r", encoding="utf-8") as html_file:
    html_content = html_file.read()

#parser = ImageParser()
#parser.feed(html_content)