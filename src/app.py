# Instalar o arquivo txt: 
# python -m venv .venv
# .\.venv\Scripts\activate.bat
# pip install --upgrade -r requirements.txt
# pip install pymysql

# Rodar o backend:
# python -m uvicorn app:app --app-dir ./src


from tempfile import template
import pymysql
import base64

from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Form, Depends, Query, UploadFile, File 
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
<<<<<<< HEAD
    "password": "ROOT",
=======
    "password": "root",
>>>>>>> e8ae198ff82c880e61b9fe51906b9d8bbe715327
    "database": "hslr"
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

app = FastAPI()

#expiração da sessão por inatividade
app.add_middleware(
    SessionMiddleware,
    secret_key="hslr",
    session_cookie="clinica_session",
    max_age = 300000000000000000000000000000000000000000000000,  #sessao expira apos 30s
    same_site="lax",
    https_only=False
)

#app.add_middleware(SessionMiddleware, secret_key="clinica")
app.mount("/static", StaticFiles(directory="static"), name="static")
pages = Jinja2Templates(directory='templates')

@app.get('/')
def index(req: Request):
    return pages.TemplateResponse(request=req, name='index.html')

#aqui tira o aviso que a sessao expirou
@app.get('/login')
def login(req: Request):

    req.session["nome_usuario"] = ''
    req.session["sobrenome_usuario"] = ''
    req.session["email_usuario"] = '' 
    req.session["numero_usuario"] = ''
    req.session["cpf_usuario"] = ''
    req.session["data_usuario"] = ''
    req.session["id_usuario"] = ''
    req.session["papel"] = ''

    expirado = req.session.pop("expirado", False)
    return pages.TemplateResponse(name='login.html', context={"expirado": expirado, "request": req})

@app.get('/calendario')
def login(req: Request):
    req.session.clear()

    expirado = req.session.pop("expirado", False)
    return pages.TemplateResponse(request=req, name='agendamento.html', context={"expirado": expirado})

#quando a sessao expira, nome_usuario vira None, redirecionando para a pagina de login
@app.get('/home')
def home(req: Request, db=Depends(get_db)):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True  # Marcar que expirou
        return RedirectResponse(url="/login", status_code=303)
    

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:               
            sql = """
                SELECT Imagem
                FROM Usuario 
                WHERE ID_usuario = %s
            """
            cursor.execute(sql, (req.session.get("id_usuario")))

            foto = cursor.fetchone()

            foto['Imagem'] = base64.b64encode(foto['Imagem']).decode('utf-8')
    finally:
        db.close()

    return pages.TemplateResponse(
        'home.html',
        {
            'request': req,
            'foto': foto,     
        }
    )

#quando a sessao expira, nome_usuario vira None, redirecionando para a pagina de login
@app.get('/homeMedico')
def homeMedico(req: Request, db=Depends(get_db)):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True  # Marcar que expirou
        return RedirectResponse(url="/login", status_code=303)
    if req.session.get("papel") != 2:
        return RedirectResponse(url="/home", status_code=303)
    
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:                              
            sql = """
                SELECT Imagem
                FROM Usuario 
                WHERE ID_usuario = %s
            """
            cursor.execute(sql, (req.session.get("id_usuario")))

            foto = cursor.fetchone()
            foto['Imagem'] = base64.b64encode(foto['Imagem']).decode('utf-8')
    finally:
        db.close()

    return pages.TemplateResponse(
        'homeMedico.html',
        {
            'request': req,
            'foto': foto,     
        }
    )

@app.get('/exames')
def exames(req: Request, cate: str = Query(default=None), db=Depends(get_db)):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True  # Marcar que expirou
        return RedirectResponse(url="/login", status_code=303)
    elif req.session.get("papel") != 3:
        return RedirectResponse(url="/home", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            #categorias para selecionar
            cursor.execute("SELECT * FROM CategoriaExame")
            categorias = cursor.fetchall()

            #busca img do usario
            sql = " SELECT Imagem FROM Usuario WHERE ID_usuario = %s"
            cursor.execute(sql, (req.session.get("id_usuario")))
            foto = cursor.fetchone()
            foto['Imagem'] = base64.b64encode(foto['Imagem']).decode('utf-8')

            #busca exames
            if cate:                                          
                sql = """
                    SELECT E.Nome, E.Descricao, E.Imagem, C.Nome AS Categoria
                    FROM Exame E
                    INNER JOIN CategoriaExame C ON C.ID_categoriaExame = E.ID_categoria
                    WHERE C.Nome = %s
                """
                cursor.execute(sql, (cate,))
            else:
                sql = """
                    SELECT E.Nome, E.Descricao, E.Imagem, C.Nome AS Categoria
                    FROM Exame E
                    INNER JOIN CategoriaExame C ON C.ID_categoriaExame = E.ID_categoria
                """
                cursor.execute(sql)

            exames = cursor.fetchall()
            for ex in exames:
                if ex['Imagem']:
                    ex['Imagem'] = base64.b64encode(ex['Imagem']).decode('utf-8')

            
    finally:
        db.close()

    return pages.TemplateResponse(
        'exames.html',
        {
            'request': req,
            'categorias': categorias,
            'exames': exames,
            'cate': cate,
            'foto': foto       
        }
    )

@app.get('/agendamentos')
def agendamentos(req: Request, db=Depends(get_db)):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True
        return RedirectResponse(url="/login", status_code=303)
    elif req.session.get("papel") != 3:
        return RedirectResponse(url="/home", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            #busca img do usuario
            cursor.execute("SELECT Imagem FROM Usuario WHERE ID_usuario = %s", (req.session.get("id_usuario"),))
            foto = cursor.fetchone()
            if foto and foto['Imagem']:
                foto['Imagem'] = base64.b64encode(foto['Imagem']).decode('utf-8')

            #busca os agendamentos do usuario
            sql = """
                SELECT Nome, Especialidade, Data, Hora
                FROM Agendamento
                WHERE ID_usuario = %s
            """
            cursor.execute(sql, (req.session.get("id_usuario"),))
            agendamentos = cursor.fetchall()

            #converte datas para string
            for ag in agendamentos:
                ag['Data'] = ag['Data'].strftime('%Y-%m-%d')

            agendamentos_json = json.dumps(agendamentos)

    finally:
        db.close()

    return template.TemplateResponse(
        'agendamentos.html',
        {
            'request': req,
            'agendamentos_json': agendamentos_json,
            'foto': foto
        }
    )

@app.post("/agendar")
def agendar_consulta(
    request: Request,
    exame_id: int = Form(...),
    medico_id: int = Form(...),
    data: str = Form(...),       # formato: yyyy-mm-dd
    hora: str = Form(...),       # formato: hh:mm
    db=Depends(get_db)
):
    #verifica se o usuário está logado
    if not request.session.get("nome_usuario"):
        request.session["expirado"] = True
        return RedirectResponse(url="/login", status_code=303)

    paciente_id = request.session.get("id_usuario")

    try:
        with db.cursor() as cursor:
            sql = """
                INSERT INTO Consulta (ID_Exame, DataConsulta, Hora, ID_medico, ID_paciente)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (exame_id, data, hora, medico_id, paciente_id))
        db.commit()
    except Exception as e:
        print("Erro ao agendar consulta:", e)
    finally:
        db.close()

    return RedirectResponse(url="/agendamentos", status_code=303)

@app.post('/cadastro')
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
    passouArroba = False
    dominioEmail = ''
    for char in email:
        if char == '@':
            passouArroba = True
        elif passouArroba:
            dominioEmail += char

    caminho = 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/default.png'

    if dominioEmail != 'hsrl.saude.br':
# --------------------------------------------------- CADASTRO PACIENTE --------------------------------------------------------------------------
        try:
            with db.cursor() as cursor:

                sql = """INSERT INTO Usuario (CPF, Email, Nome, Sobrenome, DataDeNascimento, Telefone, Senha, Imagem, Papel)
                        VALUES (%s, %s, %s, %s, %s, %s, MD5(%s), LOAD_FILE(%s), %s)"""
                cursor.execute(sql, (cpf, email, nome, sobrenome, dataNascimento, telefone, senha, caminho, 3))
                db.commit()
                
        except pymysql.MySQLError as e:

            print(e)

            if "Duplicate entry" in str(e):
                print("duplicado")
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
                    req.session["sobrenome_usuario"] = user[4] 
                    req.session["email_usuario"] = user[2] 
                    req.session["numero_usuario"] = user[6] 
                    req.session["cpf_usuario"] = user[1] 
                    req.session["data_usuario"] = user[5].strftime('%Y-%m-%d') 
                    req.session["id_usuario"] = user[0]
                    req.session["papel"] = user[9]
                    req.session["altura"] = user[10]

            db.close()

        return RedirectResponse(url='/home', status_code=303)

# --------------------------------------------- CADASTRO MÈDICO --------------------------------------------------------------------------------------
    else: 
        try:
            with db.cursor() as cursor:

                
                sql = """INSERT INTO Usuario (CPF, Email, Nome, Sobrenome, DataDeNascimento, Telefone, Senha, Imagem, Papel)
                        VALUES (%s, %s, %s, %s, %s, %s, MD5(%s), LOAD_FILE(%s), %s)"""
                cursor.execute(sql, (cpf, email, nome, sobrenome, dataNascimento, telefone, senha, caminho, 2))
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
                    req.session["sobrenome_usuario"] = user[4] 
                    req.session["email_usuario"] = user[2] 
                    req.session["numero_usuario"] = user[6] 
                    req.session["cpf_usuario"] = user[1] 
                    req.session["data_usuario"] = user[5].strftime('%Y-%m-%d') 
                    req.session["id_usuario"] = user[0]
                    req.session["papel"] = user[9]

            db.close()

        return RedirectResponse(url='/homeMedico', status_code=303)
    
# ------------------------------------------------------------- LOGIN -----------------------------------------------------------------------------------
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
                req.session["papel"] = user[9]
                req.session["foto_usuario"] = f"/usuario/foto/{user[2]}"

            else:
                req.session["errorLogin"] = "Usuário ou senha inválidos."
                req.session["errorLoginStatus"] = True
                return RedirectResponse(url="/login", status_code=303)
            
    except pymysql.MySQLError as e:
        print(e)
    finally:
        db.close()
        
    return RedirectResponse(url="/home", status_code=303)

# ---------------------------------------------------------- LOGOUT -----------------------------------------------------------------------------------
@app.get("/logout")
async def logout(request: Request):
    
    request.session.clear()  # remove os dados de sessão atual
    
    #volta pra página inicial
    return RedirectResponse(url="/", status_code=303)

# -------------------------------------------------------------------------EXCLUIR ----------------------------------------------------------
@app.post("/excluir")
async def excluir_exe(request: Request, ID_Usuario: int = Form(...), db=Depends(get_db)):
    if not request.session.get("nome_usuario"):
        request.session["expirado"] = True
        return RedirectResponse(url="/login", status_code=303)


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

# -------------------------------------------------------------------------- UPDATE USER ------------------------------------------------------------
@app.post("/atualizarUser")
async def atualizar_usuario(
    req: Request,
    ID_Usuario: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    imagem: UploadFile = File(...),
    surname: str = Form(...),
    phone: str = Form(...),
    db = Depends(get_db)
):
     
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True
        return RedirectResponse(url="/login", status_code=303)

    try:
        imagem_data = await imagem.read() 

        print(imagem)

        with db.cursor(pymysql.cursors.DictCursor) as cursor:
        
            if imagem.filename != '':
                sql_update = """
                    UPDATE Usuario 
                    SET Nome = %s, Sobrenome = %s, Email = %s, Telefone = %s, Imagem = %s
                    WHERE ID_Usuario = %s
                """
                cursor.execute(sql_update, (name, surname, email, phone, imagem_data, ID_Usuario))
            else:
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
            req.session["id_usuario"] = ID_Usuario
            req.session["mensagem_header"] = "Atualização realizada com sucesso"
            req.session["mensagem"] = "Os dados foram atualizados com sucesso."

    except Exception as e:
        req.session["mensagem_header"] = "Erro ao atualizar"
        req.session["mensagem"] = str(e)

    finally:
        db.close()

    return RedirectResponse(url="/home", status_code=303)

# -------------------------------------------------------------------- UPDATE SENHA ---------------------------------------------------------------------------
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

# ------------------------------------------------------------ FIM DE SESSÃO -----------------------------------------------------------------------------------
@app.post("/reset_session")
async def reset_session(request: Request):
    request.session.pop("mensagem_header", None)
    request.session.pop("mensagem", None)
    return {"status": "ok"}

handler = Mangum(app)

@app.route('/agendar', methods=['POST'])
def agendar():
    data = request.get_json()
    medico = data.get('medico')
    data_str = data.get('data')
    horario = data.get('horario')

    if not medico or not data_str or not horario:
        return jsonify(success=False, message='Dados incompletos'), 400

    # Verifica se o horário já está ocupado para o médico na data
    for ag in agendamentos:
        if ag['medico'] == medico and ag['data'] == data_str and ag['horario'] == horario:
            return jsonify(success=False, message='Horário já ocupado'), 400

    agendamentos.append({
        'medico': medico,
        'data': data_str,
        'horario': horario
    })

    return jsonify(success=True)