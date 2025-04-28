# Instalar o arquivo txt: pip install --upgrade -r requirements.txt
# Rodar o backend: python -m uvicorn app:app --app-dir ./src
# pip install mysql-connector-python
# python -m venv .venv
# .\.venv\Scripts\activate.bat
# pip install pymysql
# Não está na ordem

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

@app.get('/login')
def home(req: Request):
    return pages.TemplateResponse(request=req, name='login.html')

@app.get('/home')
def home(req: Request):
    return pages.TemplateResponse(request=req, name='home.html')

@app.post('/cadastro/paciente')
def cadastro(
    req: Request,
    cpf: str = Form(...),
    email: str = Form(...),
    nome: str = Form(...),
    # genero: str = Form(...),
    sobrenome: str = Form(...),
    dataNascimento: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
    db=Depends(get_db)
):
      
    try:
        with db.cursor() as cursor:
            # sql = """INSERT INTO Usuário (CPF, Email, Nome, Sobrenome, DataDeNascimento, Genero, Telefone, Senha, Papel)
            #          VALUES (%s, %s, %s, %s, %s, %s, %s, MD5(%s), %s)"""
            # cursor.execute(sql, (cpf, email, nome, sobrenome, dataNascimento, genero, telefone, senha, 3))

            sql = """INSERT INTO Usuario (CPF, Email, Nome, Sobrenome, DataDeNascimento, Telefone, Senha, Papel)
                     VALUES (%s, %s, %s, %s, %s, %s, MD5(%s), %s)"""
            cursor.execute(sql, (cpf, email, nome, sobrenome, dataNascimento, telefone, senha, 3))
            db.commit()
            
    except pymysql.MySQLError as e:

        if "Duplicate entry" in str(e):
            if "CPF" in str(e):
                msg = "Este CPF já está cadastrado."
            elif "Email" in str(e):
                msg = "Este e-mail já está cadastrado."
            else:
                msg = "Dados duplicados detectados."
        else:
            msg = "Erro ao cadastrar. Tente novamente."

        req.session["error"] = msg
        req.session["errorStatus"] = True

        return RedirectResponse(url='/login', status_code=303)

    finally:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM Usuario WHERE Email = %s AND Senha = MD5(%s)", (email, senha))
            user = cursor.fetchone()

            if user:
                req.session["nome_usuario"] = user[3] + ' ' + user[4]  

        db.close()

    return RedirectResponse(url='/home', status_code=303)

@app.post("/login")
async def login(
    req: Request,
    Login: str = Form(...),
    SenhaLogin: str = Form(...),
    db = Depends(get_db)
):
    try:
        with db.cursor() as cursor:

            cursor.execute("SELECT * FROM Usuario WHERE Email = %s AND Senha = MD5(%s)", (Login, SenhaLogin))
            user = cursor.fetchone()

            if user:
                req.session["nome_usuario"] = user[3] + ' ' + user[4]  
            else:
                req.session["errorLogin"] = "Usuário ou senha inválidos."
                req.session["errorLoginStatus"] = True
                return RedirectResponse(url="/", status_code=303)
            
    finally:
        db.close()
        
    return RedirectResponse(url="/home", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    
    request.session.clear()  # remove os dados de sessão atual
    
    #volta pra página inicial
    return RedirectResponse(url="/", status_code=303)




@app.get("/excluir")

async def excluir(request: Request, 
                  ID_usuario: int, 
                  db=Depends(get_db)):

    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/", status_code=303)

    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = ("CPF, Email, Nome, Sobrenome, DataDeNascimento, Telefone, Senha, Papel"
               "FROM Usuario"
               "WHERE ID_Usuario = %s"
               )
        
        cursor.execute(sql, (ID_usuario,))
        user = cursor.fetchone()
    db.close()

    nome_usuario = request.session.get("nome_usuario", None)

    return templates.TemplateResponse("excluir.html", {
        "request": request,
        "nome_usuario": nome_usuario,
        "user": user
    })

@app.post("/excluir_exe")
async def excluir_exe(request: Request, ID_Usuario: int = Form(...), db=Depends(get_db)):

    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            sql_delete = "DELETE FROM Usuarios WHERE ID_Usuario = %s"
            cursor.execute(sql_delete, (ID_Usuario,))
            db.commit()

            request.session["mensagem_header"] = "Exclusão do usuário"
            request.session["mensagem"] = f"Médico excluído com sucesso."

    except Exception as e:
        request.session["mensagem_header"] = "Erro ao excluir"
        request.session["mensagem"] = str(e)
    finally:
        db.close()




handler = Mangum(app)