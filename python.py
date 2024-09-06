from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory='templates')

@app.post('/disable/{name}')
def disable_cat(name: str):
    print(name)
    return f'{name} category has been disabled.'

@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('lol.html', {'request': request})