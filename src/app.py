# Instalar o arquivo txt: pip install --upgrade -r requirements.txt
# Rodar o backend: python -m uvicorn app:app --app-dir ./src

from typing import Annotated
from fastapi import FastAPI, Form
from forms import LoginForm
from mangum import Mangum
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()

pages = Jinja2Templates(directory='templates')

@app.get('/')
def home(req: Request):
    return pages.TemplateResponse(request=req, name='index.html')

@app.post('/login')
def cadastro(req: Request, form: Annotated[LoginForm, Form()]):
    page = 'sucess.html'
    context = {'emailcadastro': form.email}
    return pages.TemplateResponse(request=req, name=page, context=context)


handler = Mangum(app)