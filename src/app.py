# Instalar o arquivo txt: 
# python -m venv .venv
# .\.venv\Scripts\activate.bat
# pip install --upgrade -r requirements.txt
# pip install pymysql

# Rodar o backend:
#  python -m uvicorn app:app --app-dir ./src


# subir imagem do usuário (usar blob) (mediumblob) (sprint 3)

import pymysql

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
app.add_middleware(
    SessionMiddleware,
    secret_key="clinica", 
    max_age = 50
 )
app.mount("/static", StaticFiles(directory="static"), name="static")
pages = Jinja2Templates(directory='templates')


@app.get('/')
def index(req: Request):
    return pages.TemplateResponse(request=req, name='index.html')

@app.get('/login')
def login(req: Request):
    return pages.TemplateResponse(request=req, name='login.html')

@app.get('/home')
def home(req: Request):
    return pages.TemplateResponse(request=req, name='home.html')

@app.get('/exames')
def exames(req: Request):
    return pages.TemplateResponse(request=req, name='exames.html')


@app.post('/cadastro/paciente')
def cadastro(
    req: Request,
    cpf: str = Form(...),
    email: str = Form(...),
    nome: str = Form(...),
    idade: str = Form(...),
    sobrenome: str = Form(...),
    dataNascimento: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
    db=Depends(get_db)
):
      
    try:
        with db.cursor() as cursor:

            sql = """INSERT INTO Usuario (CPF, Email, Nome, Sobrenome, DataDeNascimento, Idade, Telefone, Senha, Papel)
                     VALUES (%s, %s, %s, %s, %s, %s,  %s, MD5(%s), %s)"""
            cursor.execute(sql, (cpf, email, nome, sobrenome, dataNascimento, idade, telefone, senha, 3))
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
                req.session["nome_usuario"] = user[3]

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
                req.session["nome_usuario"] = user[3] 
                req.session["sobrenome_usuario"] = user[4] 
                req.session["email_usuario"] = user[2] 
                req.session["numero_usuario"] = user[6] 
                req.session["cpf_usuario"] = user[1] 
                req.session["data_usuario"] = user[5].strftime('%Y-%m-%d') 
                req.session["id_usuario"] = user[0]
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


@app.post("/excluir")
async def excluir_exe(request: Request, ID_Usuario: int = Form(...), db=Depends(get_db)):

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            sql_delete = "DELETE FROM Usuario WHERE ID_Usuario = %s"
            cursor.execute(sql_delete, (ID_Usuario,))
            db.commit()

            request.session["mensagem_header"] = "Exclusão do usuário"
            request.session["mensagem"] = f"Médico excluído com sucesso."

    except Exception as e:
        request.session["mensagem_header"] = "Erro ao excluir"
        request.session["mensagem"] = str(e)
    finally:
        db.close()

    return RedirectResponse(url="/", status_code=303)


@app.post("/atualizar")
async def atualizar_usuario(
    req: Request,
    ID_Usuario: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    surname: str = Form(...),
    phone: str = Form(...),
    db = Depends(get_db)
):
    try:
        # Atualizar os dados do usuário

        print("ID:", ID_Usuario)
        print("Nome:", name)
        print("Email:", email)

        with db.cursor(pymysql.cursors.DictCursor) as cursor:
        
            sql_update = """
                UPDATE Usuario 
                SET Nome = %s, Sobrenome = %s, Email = %s, Telefone = %s 
                WHERE ID_Usuario = %s
            """
            cursor.execute(sql_update, (name, surname, email, phone, ID_Usuario))
        
            db.commit()

            req.session["nome_usuario"] = name 
            req.session["sobrenome_usuario"] = surname 
            req.session["email_usuario"] = email 
            req.session["numero_usuario"] = phone
            req.session["mensagem_header"] = "Atualização realizada com sucesso"
            req.session["mensagem"] = "Os dados foram atualizados com sucesso."

    except Exception as e:
        req.session["mensagem_header"] = "Erro ao atualizar"
        req.session["mensagem"] = str(e)

    finally:
        db.close()

    return RedirectResponse(url="/home", status_code=303)

@app.post("/novaSenha")
async def atualizar_usuario(
    req: Request,
    cpfconfir: int = Form(...),
    novasenha: str = Form(...),
    novaconfirmarsenhacadastro: str = Form(...),
    db = Depends(get_db)
):
    try:

        with db.cursor(pymysql.cursors.DictCursor) as cursor:
        
            sql_update = """
                UPDATE Usuario 
                SET Senha = MD5(%s)
                WHERE CPF = %s
            """
            cursor.execute(sql_update, (novasenha, cpfconfir))
        
            db.commit()

    except Exception as e:
        req.session["mensagem_header"] = "Erro ao atualizar"
        req.session["mensagem"] = str(e)

    finally:
        db.close()

    return RedirectResponse(url="/", status_code=303)

handler = Mangum(app)