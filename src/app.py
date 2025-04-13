# Instalar o arquivo txt: pip install --upgrade -r requirements.txt
# Rodar o backend: python -m uvicorn app:app --app-dir ./src
# pip install mysql-connector-python

# user md5 (criptografar senha)
# ligar pastas de java e css como static
# aparecer o nome e poder deslogar
# cadastro
# subir imagem do usuário (usar blob) (mediumblob) (sprint 3)

import pymysql
import base64

from typing import Annotated
from fastapi import FastAPI, Form, Depends
from forms import UserForm
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
from starlette.requests import Request
from starlette.templating import Jinja2Templates

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "hslr"
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

pages = Jinja2Templates(directory='templates')

@app.get('/')
def home(req: Request):
    return pages.TemplateResponse(request=req, name='index.html')

@app.post('/cadastro/paciente')
def cadastro(
    req: Request,
    cpf: str = Form(...),
    email: str = Form(...),
    nome: str = Form(...),
    sobrenome: str = Form(...),
    dataNascimento: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
    db=Depends(get_db)
):
    
    print("RECEBIDO:", cpf, email, nome, sobrenome, dataNascimento, telefone, senha)

    try:
        with db.cursor() as cursor:
            sql = """INSERT INTO Usuário (CPF, Email, Nome, Sobrenome, DataDeNascimento, Genero, Telefone, Senha, Papel)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, MD5(%s), %s)"""
            cursor.execute(sql, (cpf, email, nome, sobrenome, dataNascimento, 'genero', telefone, senha, 3))
            db.commit()
    finally:
        db.close()

    return pages.TemplateResponse("success.html", {"request": req, "emailcadastro": email})


handler = Mangum(app)
