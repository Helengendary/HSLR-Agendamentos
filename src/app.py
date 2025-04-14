# Instalar o arquivo txt: pip install --upgrade -r requirements.txt
# Rodar o backend: python -m uvicorn app:app --app-dir ./src
# pip install mysql-connector-python

# user md5 (criptografar senha)
# aparecer o nome e poder deslogar
# cadastro
# subir imagem do usuário (usar blob) (mediumblob) (sprint 3)

import pymysql
import base64

from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Form, Depends
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "hslr"
}

def get_db():
    return pymysql.connect(**DB_CONFIG)


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="clinica")
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
    genero: str = Form(...),
    sobrenome: str = Form(...),
    dataNascimento: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
    db=Depends(get_db)
):
      
    try:
        with db.cursor() as cursor:
            sql = """INSERT INTO Usuário (CPF, Email, Nome, Sobrenome, DataDeNascimento, Genero, Telefone, Senha, Papel)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, MD5(%s), %s)"""
            cursor.execute(sql, (cpf, email, nome, sobrenome, dataNascimento, genero, telefone, senha, 3))
            db.commit()
    except pymysql.err.IntegrityError as e:
        
        erro = str(e)
        if "Duplicate entry" in erro:
            if "CPF" in erro:
                msg = "Este CPF já está cadastrado."
            elif "Email" in erro:
                msg = "Este e-mail já está cadastrado."
            else:
                msg = "Dados duplicados detectados."
        else:
            msg = "Erro ao cadastrar. Tente novamente."

        return pages.TemplateResponse("index.html", {
            "request": req,
            "error": msg
        })
    finally:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM Usuário WHERE Email = %s AND Senha = MD5(%s)", (email, senha))
            user = cursor.fetchone()

            req.session["nome_usuario"] = user[3] + ' ' + user[4]  
            return pages.TemplateResponse("success.html", {"request": req})

        db.close()

    return pages.TemplateResponse("success.html", {"request": req, "emailcadastro": email})

@app.post("/login")
async def login(
    req: Request,
    Login: str = Form(...),
    SenhaLogin: str = Form(...),
    db = Depends(get_db)
):
    try:
        with db.cursor() as cursor:

            cursor.execute("SELECT * FROM Usuário WHERE Email = %s AND Senha = MD5(%s)", (Login, SenhaLogin))
            user = cursor.fetchone()

            if user:
                req.session["nome_usuario"] = user[3] + ' ' + user[4]  
                return pages.TemplateResponse("success.html", {"request": req})
            else:
                req.session["errorLogin"] = "Usuário ou senha inválidos."
                req.session["errorLoginStatus"] = True
                return RedirectResponse(url="/", status_code=303)
    finally:
        db.close()



handler = Mangum(app)