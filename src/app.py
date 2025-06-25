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

from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi import FastAPI, Form, Depends, Path, Query, UploadFile, File 
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from datetime import date, datetime, time, timedelta
from starlette.middleware.sessions import SessionMiddleware
from utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
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
    max_age = 10,  #sessao expira apos 30s
    same_site="lax",
    https_only=False
)

#app.add_middleware(SessionMiddleware, secret_key="clinica")
app.mount("/static", StaticFiles(directory="static"), name="static")
pages = Jinja2Templates(directory='templates')

@app.get('/')
def index(req: Request):
    return pages.TemplateResponse(request=req, name='index.html')

@app.get('/agendamentos', response_class=HTMLResponse)
def index(req: Request, db=Depends(get_db)):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True  # Marcar que expirou
        return RedirectResponse(url="/login", status_code=303)
    if req.session.get("papel") != 3:
        return RedirectResponse(url="/homeMedico", status_code=303)

    agendamentos_json_para_frontend = []
    horarios = ["09:00:00", "09:30:00", "10:00:00", "10:30:00", "11:00:00", "11:30:00", "13:00:00", "13:30:00", "14:00:00", "14:30:00", "15:00:00", "15:30:00", "16:00:00", "16:30:00", "17:00:00", "17:30:00"]

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Exame")
            exames = cursor.fetchall()

            cursor.execute("SELECT * FROM Usuario WHERE email LIKE '%hslr.saude.br';")
            medicos = cursor.fetchall()

            cursor.execute("SELECT ID_medico, Hora FROM consulta;")
            horas = cursor.fetchall()

            cursor.execute("""
                SELECT 
                A.DataConsulta, 
                A.Hora, 
                A.ID_medico,
                E.Nome AS Exame_Nome,
                M.Nome AS Medico_Nome,
                M.Sobrenome AS Medico_Sobrenome
                FROM consulta AS A
                JOIN Exame AS E ON A.ID_exame = E.ID_exame
                JOIN Usuario AS M ON A.ID_medico = M.ID_usuario
                WHERE A.ID_paciente = %s
                ORDER BY A.DataConsulta, A.Hora;
            """, (req.session.get("ID_usuario"),))
            agendamentos_usuario_logado = cursor.fetchall()

            print(req.session.get("ID_usuario"),)

            for ag in agendamentos_usuario_logado:
                data_formatada = None
                if ag['DataConsulta']:
                    if isinstance(ag['DataConsulta'], date):
                        data_formatada = ag['DataConsulta'].strftime('%Y-%m-%d')
                    else: 
                        try:
                            data_formatada = date.fromisoformat(str(ag['DataConsulta'])).strftime('%Y-%m-%d')
                        except ValueError:
                            print(f"DEBUG: Data inválida para formatação: {ag['DataConsulta']}")

                hora_formatada = None
                hora_obj = ag['Hora']

                if isinstance(hora_obj, time):
                    hora_formatada = hora_obj.strftime('%H:%M')
                elif isinstance(hora_obj, timedelta):
                    total_seconds = int(hora_obj.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    hora_formatada = f"{hours:02}:{minutes:02}" 
                elif isinstance(hora_obj, datetime):
                    hora_formatada = hora_obj.strftime('%H:%M')
                elif isinstance(hora_obj, str):
                    try:
                        hora_formatada = datetime.strptime(hora_obj, '%H:%M:%S').strftime('%H:%M')
                    except ValueError:
                        try:
                            hora_formatada = datetime.strptime(hora_obj, '%H:%M').strftime('%H:%M')
                        except ValueError:
                            print(f"DEBUG HORA: Formato de hora em string inesperado: {hora_obj}")
                            hora_formatada = None 

                if data_formatada and hora_formatada:
                    agendamentos_json_para_frontend.append({
                        'data': data_formatada,
                        'hora': hora_formatada,
                        'especialidade': ag.get('Exame_Nome', 'Exame Desconhecido'),
                        'descricao': f"Consulta com Dr(a). {ag.get('Medico_Nome', '')} {ag.get('Medico_Sobrenome', '')}"
                    })
                else:
                    print(f"AVISO: Agendamento incompleto ou com data/hora inválida, ignorado: {ag}. Data formatada: {data_formatada}, Hora formatada: {hora_formatada}")

    except pymysql.MySQLError as e:
        print(f"ERRO MySQL na rota /agendamentos: {e}")
        req.session["mensagem_header"] = "Erro no Banco de Dados"
        req.session["mensagem"] = "Não foi possível carregar agendamentos. Tente novamente."
        return pages.TemplateResponse(
            'agendamento.html',
            {
                'request': req,
                'exames': [], 
                'medicos': [],
                'horario_funcionamento': horarios,
                'agendamentos_usuario_logado_json': []
            }
        )
    except Exception as e:
        print(f"ERRO INESPERADO na rota /agendamentos: {e}")
        req.session["mensagem_header"] = "Erro Inesperado"
        req.session["mensagem"] = "Ocorreu um erro ao carregar a página de agendamentos."
        return pages.TemplateResponse(
            'agendamento.html',
            {
                'request': req,
                'exames': [],
                'medicos': [],
                'horario_funcionamento': horarios,
                'agendamentos_usuario_logado_json': []
            }
        )
    finally:
        db.close()

    print(f"DEBUG PYTHON: Agendamentos para o frontend: {agendamentos_json_para_frontend}") # <--- ADICIONE ESTE PRINT
    print(f"DEBUG PYTHON: Quantidade de agendamentos: {len(agendamentos_json_para_frontend)}") # <--- ADICIONE ESTE PRINT

    return pages.TemplateResponse(
        'agendamento.html',
        {
            'request': req,
            'exames': exames,
            'medicos': medicos,
            'horario_funcionamento': horarios,
            'agendamentos_usuario_logado_json': agendamentos_json_para_frontend
        }
    )

@app.get('/agenda')
def index(req: Request, db=Depends(get_db)):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True  # Marcar que expirou
        return RedirectResponse(url="/login", status_code=303)
    if req.session.get("papel") != 2:
        return RedirectResponse(url="/home", status_code=303)

    agendamentos_para_frontend = {}

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT C.DataConsulta 
                FROM Consulta C 
                WHERE ID_medico = %s
                ORDER BY C.DataConsulta;
            """, (req.session.get("ID_usuario"),))
            agendamentos_usuario_logado = cursor.fetchall()

            cursor.execute("""
                SELECT C.Hora AS Hora ,
                C.ID_consulta AS ID_consulta,
                C.DataConsulta AS DataConsulta,
                U.Nome AS NomePaciente,
                U.Sobrenome AS SobrenomePaciente,
                E.Nome AS NomeExame
                FROM Consulta C 
                INNER JOIN Usuario U ON U.ID_usuario = C.ID_paciente
                INNER JOIN Exame E ON E.ID_exame = C.ID_exame
                WHERE ID_medico = %s;
            """, (req.session.get("ID_usuario"),))
            consultas = cursor.fetchall()

            for ag in agendamentos_usuario_logado:
                consultas_current = []
                for conCurrent in consultas:
                    if ag['DataConsulta'] == conCurrent['DataConsulta']:

                        hora_formatada = None
                        hora_obj = conCurrent['Hora']
                        if isinstance(hora_obj, time):
                            hora_formatada = hora_obj.strftime('%H:%M')
                        elif isinstance(hora_obj, timedelta):
                            total_seconds = int(hora_obj.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            hora_formatada = f"{hours:02}:{minutes:02}" 
                        elif isinstance(hora_obj, datetime):
                            hora_formatada = hora_obj.strftime('%H:%M')
                        elif isinstance(hora_obj, str):
                            try:
                                hora_formatada = datetime.strptime(hora_obj, '%H:%M:%S').strftime('%H:%M')
                            except ValueError:
                                try:
                                    hora_formatada = datetime.strptime(hora_obj, '%H:%M').strftime('%H:%M')
                                except ValueError:
                                    print(f"DEBUG HORA: Formato de hora em string inesperado: {hora_obj}")
                                    hora_formatada = None 


                        consultas_current.append({'Hora': hora_formatada, 'NomePaciente': f'{conCurrent['NomePaciente']} {conCurrent['SobrenomePaciente']}', 'NomeExame': conCurrent['NomeExame'], 'ID_consulta': conCurrent['ID_consulta']})

                data_formatada = None
                if ag['DataConsulta']:
                    if isinstance(ag['DataConsulta'], date):
                        data_formatada = ag['DataConsulta'].strftime('%d-%m-%Y')
                    else: 
                        try:
                            data_formatada = date.fromisoformat(str(ag['DataConsulta'])).strftime('%d-%m-%Y')
                        except ValueError:
                            print(f"DEBUG: Data inválida para formatação: {ag['DataConsulta']}")
                
                agendamentos_para_frontend.update({data_formatada:consultas_current})


    except pymysql.MySQLError as e:
        print(f"ERRO MySQL na rota /agendamentos: {e}")
        req.session["mensagem_header"] = "Erro no Banco de Dados"
        req.session["mensagem"] = "Não foi possível carregar agendamentos. Tente novamente."
        return pages.TemplateResponse(
            'agendamento.html',
            {
                'request': req,
                'agendamentos_usuario_logado_json': {}
            }
        )
    except Exception as e:
        print(f"ERRO INESPERADO na rota /agendamentos: {e}")
        req.session["mensagem_header"] = "Erro Inesperado"
        req.session["mensagem"] = "Ocorreu um erro ao carregar a página de agendamentos."
        return pages.TemplateResponse(
            'agendamento.html',
            {
                'request': req,
                'agendamentos_usuario_logado_json': {}
            }
        )
    finally:
        db.close()

    return pages.TemplateResponse(
        'agendaMedico.html',
        {
            'request': req,
            'exames': agendamentos_para_frontend
        }
    )

@app.get('/api/agendamentos_por_dia', response_class=JSONResponse)
async def get_agendamentos_por_dia(
    req: Request,
    selected_date: str = Query(..., description="Data selecionada no formato YYYY-MM-DD"),
    db=Depends(get_db)
):
    user_id = req.session.get('ID_usuario')

    if not user_id:
        return JSONResponse(status_code=401, content={"success": False, "message": "Usuário não autenticado."})

    try:
        data_obj = date.fromisoformat(selected_date)

        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT
                    A.ID_consulta,
                    A.DataConsulta,
                    A.Hora, 
                    E.Nome AS Exame_Nome,
                    E.Descricao AS Exame_Descricao,
                    U.Nome AS Medico_Nome,
                    U.Sobrenome AS Medico_Sobrenome
                FROM
                    Consulta AS A
                JOIN
                    Exame AS E ON A.ID_exame = E.ID_exame
                JOIN
                    Usuario AS U ON A.ID_medico = U.ID_usuario
                WHERE
                    A.ID_paciente = %s AND A.DataConsulta = %s
                ORDER BY
                    A.Hora;
            """
            cursor.execute(sql, (user_id, data_obj))
            agendamentos_do_dia = cursor.fetchall()

        formatted_agendamentos = []
        for agendamento in agendamentos_do_dia:
            hora_obj = agendamento['Hora']
            hora_formatada = None

            if isinstance(hora_obj, time): 
                hora_formatada = hora_obj.strftime('%H:%M')
            elif isinstance(hora_obj, timedelta):
                # Converter timedelta para string HH:MM
                total_seconds = int(hora_obj.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                hora_formatada = f"{hours:02}:{minutes:02}"
            elif isinstance(hora_obj, datetime): 
                hora_formatada = hora_obj.strftime('%H:%M')
            elif isinstance(hora_obj, str): 
                try:
                    hora_formatada = datetime.strptime(hora_obj, '%H:%M:%S').strftime('%H:%M')
                except ValueError:
                    try:
                        hora_formatada = datetime.strptime(hora_obj, '%H:%M').strftime('%H:%M')
                    except ValueError:
                        print(f"DEBUG: Formato de hora em string inesperado: {hora_obj}")
                        hora_formatada = None 

            # Verificação de DataConsulta também, para garantir
            data_consulta_obj = agendamento['DataConsulta']
            data_formatada = None
            if isinstance(data_consulta_obj, date):
                data_formatada = data_consulta_obj.strftime('%Y-%m-%d')
            elif isinstance(data_consulta_obj, datetime):
                data_formatada = data_consulta_obj.strftime('%Y-%m-%d')
            elif isinstance(data_consulta_obj, str):
                try:
                    data_formatada = date.fromisoformat(data_consulta_obj).strftime('%Y-%m-%d')
                except ValueError:
                    print(f"DEBUG: Formato de data em string inesperado: {data_consulta_obj}")
                    data_formatada = None 


            # Adiciona o agendamento formatado se a hora e a data forem válidas
            if hora_formatada and data_formatada:
                formatted_agendamentos.append({
                    "id": agendamento['ID_consulta'],
                    "data": data_formatada,
                    "hora": hora_formatada,
                    "exame_nome": agendamento['Exame_Nome'],
                    "exame_descricao": agendamento['Exame_Descricao'],
                    "medico_nome": f"Dr(a). {agendamento['Medico_Nome']} {agendamento['Medico_Sobrenome']}"
                })
            else:
                print(f"AVISO: Agendamento com data/hora inválida ignorado na formatação: {agendamento}")


        return JSONResponse(status_code=200, content={"success": True, "agendamentos": formatted_agendamentos})

    except ValueError:
        return JSONResponse(status_code=400, content={"success": False, "message": "Formato de data inválido. Use YYYY-MM-DD."})
    except pymysql.MySQLError as e:
        print(f"Erro no banco de dados ao buscar agendamentos: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": "Erro no servidor ao buscar agendamentos."})
    except Exception as e:
        print(f"Erro inesperado ao buscar agendamentos: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": "Ocorreu um erro inesperado."})

# ---  BUSCAR HORÁRIOS OCUPADOS PARA UM MÉDICO E DATA ESPECÍFICA ---
@app.get('/api/horarios_ocupados', response_class=JSONResponse)
async def get_horarios_ocupados(
    req: Request,
    medico_id: int = Query(..., description="ID do médico"),
    selected_date: str = Query(..., description="Data selecionada no formato YYYY-MM-DD"),
    db=Depends(get_db)
):
    try:
        data_obj = date.fromisoformat(selected_date)

        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT Hora
                FROM consulta
                WHERE ID_medico = %s AND DataConsulta = %s;
            """
            cursor.execute(sql, (medico_id, data_obj))
            horarios_ocupados_db = cursor.fetchall()

            ocupados_list = []
            for hr in horarios_ocupados_db:
                hora_obj = hr['Hora']
                hora_formatada = None

                if isinstance(hora_obj, time): 
                    hora_formatada = hora_obj.strftime('%H:%M')
                elif isinstance(hora_obj, timedelta): 
                    total_seconds = int(hora_obj.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    hora_formatada = f"{hours:02}:{minutes:02}"
                elif isinstance(hora_obj, datetime): 
                    hora_formatada = hora_obj.strftime('%H:%M')
                elif isinstance(hora_obj, str):
                    try:
                        hora_formatada = datetime.strptime(hora_obj, '%H:%M:%S').strftime('%H:%M')
                    except ValueError:
                        try:
                            hora_formatada = datetime.strptime(hora_obj, '%H:%M').strftime('%H:%M')
                        except ValueError:
                            print(f"DEBUG: Formato de hora em string inesperado em horarios_ocupados: {hora_obj}")
                            hora_formatada = None # Fallback
                
                if hora_formatada:
                    ocupados_list.append(hora_formatada)
                else:
                    print(f"AVISO: Hora inválida no banco de dados para medico_id {medico_id}, data {selected_date}: {hr['Hora']}")


        return JSONResponse(status_code=200, content={"success": True, "ocupados": ocupados_list})

    except ValueError:
        return JSONResponse(status_code=400, content={"success": False, "message": "Formato de data ou ID de médico inválido."})
    except pymysql.MySQLError as e:
        print(f"Erro no banco de dados ao buscar horários ocupados: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": "Erro no servidor ao buscar horários ocupados."})
    except Exception as e:
        print(f"Erro inesperado ao buscar horários ocupados: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": "Ocorreu um erro inesperado."})

@app.get("/setar_medico")
def setar_medico(id: int, req: Request):
    req.session["medico_selecionado"] = id
    return RedirectResponse(url="/agendamentos", status_code=303)

#aqui tira o aviso que a sessao expirou
@app.get('/login')
def login(req: Request):

    req.session["nome_usuario"] = ''
    req.session["sobrenome_usuario"] = ''
    req.session["email_usuario"] = '' 
    req.session["numero_usuario"] = ''
    req.session["cpf_usuario"] = ''
    req.session["data_usuario"] = ''
    req.session["ID_usuario"] = ''
    req.session["papel"] = ''

    expirado = req.session.pop("expirado", False)
    return pages.TemplateResponse(name='login.html', context={"expirado": expirado, "request": req})

#quando a sessao expira, nome_usuario vira None, redirecionando para a pagina de login
@app.get('/home')
def home(req: Request, db=Depends(get_db)):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True  # Marcar que expirou
        return RedirectResponse(url="/login", status_code=303)
    if req.session.get("papel") != 3:
        return RedirectResponse(url="/homeMedico", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:               
            sql = """
                SELECT Imagem
                FROM Usuario 
                WHERE ID_usuario = %s
            """
            cursor.execute(sql, (req.session.get("ID_usuario")))

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
            cursor.execute(sql, (req.session.get("ID_usuario")))

            foto = cursor.fetchone()
            foto['Imagem'] = base64.b64encode(foto['Imagem']).decode('utf-8')
            
            sql = """
                SELECT COUNT(ID_medico) AS TotalConsulta 
                FROM Consulta C 
                WHERE ID_medico = %s;
            """
            cursor.execute(sql, (req.session.get("ID_usuario")))
            total = cursor.fetchone()
           
            sql = """
              SELECT C.Hora AS Hora, U.Nome AS Nome 
              FROM Consulta C 
              INNER JOIN Usuario U ON U.ID_usuario = C.ID_paciente 
              WHERE C.ID_medico = %s
              ORDER BY C.DataConsulta, C.Hora 
              LIMIT 1;
            """
            cursor.execute(sql, (req.session.get("ID_usuario")))
            proxima = cursor.fetchone()
    finally:
        db.close()

    return pages.TemplateResponse(
        'homeMedico.html',
        {
            'request': req,
            'foto': foto,
            'totalConsulta' : total,     
            'proximaConsulta' : proxima,     
        }
    )

@app.get('/exames')
def exames(req: Request, cate: str = Query(default=None), db=Depends(get_db)):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True  # Marcar que expirou
        return RedirectResponse(url="/login", status_code=303)
    

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            #categorias para selecionar
            cursor.execute("SELECT * FROM CategoriaExame")
            categorias = cursor.fetchall()

            #busca img do usario
            sql = " SELECT Imagem FROM Usuario WHERE ID_usuario = %s"
            cursor.execute(sql, (req.session.get("ID_usuario")))
            foto = cursor.fetchone()
            foto['Imagem'] = base64.b64encode(foto['Imagem']).decode('utf-8')

            #busca exames
            if cate:                                          
                sql = """
                    SELECT E.ID_exame, E.Nome, E.Descricao, E.Imagem, C.Nome AS Categoria
                    FROM Exame E
                    INNER JOIN CategoriaExame C ON C.ID_categoriaExame = E.ID_categoria
                    WHERE C.ID_categoriaExame = %s;
                """

                cursor.execute(sql, (cate))
            else:
                sql = """
                    SELECT E.ID_exame, E.Nome, E.Descricao, E.Imagem, C.Nome AS Categoria
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

@app.get('/acharMedico')
def achar(req: Request, db=Depends(get_db)):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True  # Marcar que expirou
        return RedirectResponse(url="/login", status_code=303)
    if req.session.get("papel") != 3:
        return RedirectResponse(url="/homeMedico", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            #busca img do usario
            sql = " SELECT Imagem FROM Usuario WHERE ID_usuario = %s"
            cursor.execute(sql, (req.session.get("ID_usuario")))
            foto = cursor.fetchone()
            foto['Imagem'] = base64.b64encode(foto['Imagem']).decode('utf-8')
                                    
            sql = """
                SELECT Nome, Sobrenome, Email, Telefone, Imagem 
                FROM Usuario 
                WHERE Email LIKE '%hslr.saude.br';
            """

            cursor.execute(sql)

            doctores = cursor.fetchall()
            for ex in doctores:
                if ex['Imagem']:
                    ex['Imagem'] = base64.b64encode(ex['Imagem']).decode('utf-8')

            
    finally:
        db.close()

    return pages.TemplateResponse(
        'doutores.html',
        {
            'request': req,
            'doutores': doctores,
            'foto': foto       
        }
    )

@app.post('/excluirExame')
def excluirExames(
    request: Request,
    excluirID: str = Form(...),
    db=Depends(get_db)
):
    if not request.session.get("nome_usuario"):
        request.session["expirado"] = True  # Marcar que expirou
        return RedirectResponse(url="/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            sql_delete = "DELETE FROM Exame WHERE ID_exame = %s"
            cursor.execute(sql_delete, (excluirID,))
            db.commit()

            request.session["mensagem_header"] = "Exclusão do exame"
            request.session["mensagem"] = f"Exame excluído com sucesso."

    except Exception as e:
        request.session["mensagem_header"] = "Erro ao excluir"
        request.session["mensagem"] = str(e)
    finally:
        db.close()

    return RedirectResponse(url="/exames", status_code=303)          

@app.post('/addExame')
async def addExame(
    req: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    imagem:  UploadFile = File(...),
    cate: str = Form(...),
    db=Depends(get_db)
):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True
        return RedirectResponse(url="/login", status_code=303)


    try:
        image_content = await imagem.read()

        print(imagem)

        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            if imagem.filename != '':
                sql = """INSERT INTO Exame (Nome, Descricao, Imagem, ID_categoria)
                        VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (nome, descricao, image_content, cate))
            else:
                caminho = 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/padraoexame.png'

                sql = """INSERT INTO Exame (Nome, Descricao, Imagem, ID_categoria)
                        VALUES (%s, %s, LOAD_FILE(%s), %s)"""
                cursor.execute(sql, (nome, descricao, caminho, cate))

            db.commit()
            
    except pymysql.MySQLError as e:

        print(e)

        if "Duplicate entry" in str(e):
            msg = "Nome duplicados."
        else:
            msg = "Erro ao cadastrar. Tente novamente."

        req.session["errorAddExames"] = msg
        req.session["errorStatusAddExames"] = True

        return RedirectResponse(url='/exames', status_code=303)

    finally:
        db.close()

    return RedirectResponse(url='/exames', status_code=303)

@app.post('/editarExame')
async def editarExame(
    req: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    imagem:  UploadFile = File(...),
    cate: str = Form(...),
    ID_exame: str = Form(...),
    db=Depends(get_db)
):
    if not req.session.get("nome_usuario"):
        req.session["expirado"] = True
        return RedirectResponse(url="/login", status_code=303)


    try:
        image_content = await imagem.read()

        print(ID_exame)

        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            if imagem.filename != '':
                sql = """
                    UPDATE Exame 
                    SET Nome = %s, Descricao = %s, Imagem = %s, ID_categoria = %s
                    WHERE ID_exame = %s"""
                cursor.execute(sql, (nome, descricao, image_content, cate, ID_exame))
            else:

                sql = """
                    UPDATE Exame 
                    SET Nome = %s, Descricao = %s, ID_categoria = %s
                    WHERE ID_exame = %s"""
                cursor.execute(sql, (nome, descricao, cate, ID_exame))

            db.commit()
            
    except pymysql.MySQLError as e:
        print(f"ERRO no banco de dados (MySQL) /editarExame: {e}")
        if "Duplicate entry" in str(e):
            msg = "Nome do exame duplicado."
        else:
            msg = "Erro ao atualizar o exame. Tente novamente."

        req.session["errorAddExames"] = msg
        req.session["errorStatusAddExames"] = True

        return RedirectResponse(url='/exames', status_code=303)
    except Exception as e:
        print(f"ERRO inesperado /editarExame: {e}")
        req.session["errorAddExames"] = "Ocorreu um erro inesperado ao atualizar o exame."
        req.session["errorStatusAddExames"] = True
        return RedirectResponse(url='/exames', status_code=303)
    finally:
        db.close()

    return RedirectResponse(url='/exames', status_code=303)

@app.post("/agendar")
def agendar_consulta(
    request: Request,
    exame: int = Form(...),
    medico: int = Form(...),
    data: str = Form(...),       
    horario: str = Form(...),     
    db=Depends(get_db)
):
    #verifica se o usuário está logado
    if not request.session.get("nome_usuario"):
        request.session["expirado"] = True
        return RedirectResponse(url="/login", status_code=303)

    paciente_id = request.session.get("ID_usuario")

    try:
        with db.cursor() as cursor:
            sql = """
                INSERT INTO Consulta (ID_Exame, DataConsulta, Hora, ID_medico, ID_paciente)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (exame, data, horario, medico, paciente_id))
        db.commit()
    except Exception as e:
        print("Erro ao agendar consulta:", e)
    finally:
        db.close()

    return RedirectResponse(url="/agendamentos", status_code=303)

@app.delete('/api/agendamentos/{appointment_id}', response_class=JSONResponse)
async def cancel_appointment(
    req: Request,
    appointment_id: int = Path(..., description="ID da consulta a ser cancelada"),
    db=Depends(get_db)
):
    user_id = req.session.get('ID_usuario')

    if not user_id:
        return JSONResponse(status_code=401, content={"success": False, "message": "Usuário não autenticado."})

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            cursor.execute("""
                DELETE FROM Consulta
                WHERE ID_consulta = %s;
            """, (appointment_id,))
            db.commit()

            if cursor.rowcount == 0:
                return JSONResponse(status_code=500, content={"success": False, "message": "Nenhum agendamento foi cancelado. Tente novamente."})

        return JSONResponse(status_code=200, content={"success": True, "message": "Agendamento cancelado com sucesso!"})

    except pymysql.MySQLError as e:
        db.rollback() 
        print(f"Erro no banco de dados ao cancelar agendamento: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": "Erro no servidor ao cancelar agendamento. Tente novamente."})
    except Exception as e:
        db.rollback() 
        print(f"Erro inesperado ao cancelar agendamento: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": "Ocorreu um erro inesperado ao cancelar o agendamento."})

#------------------------------------------------------------------ CADASTRO --------------------------------------------------------------------------
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

    caminho = 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/default.webp'
    
    redirect_url = '/login'
    status_code = 303

    papel = 2

    if dominioEmail != 'hslr.saude.br':
        papel = 3

    hashed_senha = get_hashed_password(senha)

    try:
        with db.cursor() as cursor:
           
            sql = """INSERT INTO Usuario (CPF, Email, Nome, Sobrenome, DataDeNascimento, Telefone, Senha, Imagem, Papel)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, LOAD_FILE(%s), %s)"""
            cursor.execute(sql, (cpf, email, nome, sobrenome, dataNascimento, telefone, hashed_senha, caminho, papel))
            
            db.commit()

            cursor.execute("SELECT * FROM Usuario WHERE Email = %s", (email))
            user = cursor.fetchone()

            if user:
                req.session["nome_usuario"] = user[3] 
                req.session["sobrenome_usuario"] = user[4] 
                req.session["email_usuario"] = user[2] 
                req.session["numero_usuario"] = user[6] 
                req.session["cpf_usuario"] = user[1] 
                req.session["data_usuario"] = user[5].strftime('%Y-%m-%d') 
                req.session["ID_usuario"] = user[0]
                req.session["papel"] = user[9]
                req.session["foto_usuario"] = f"/usuario/foto/{user[2]}"

                access_token = create_access_token(user[2])
                req.session["access_token"] = access_token
                req.session["token_type"] = 'bearer'

                if papel == 3:
                    redirect_url= '/home'
                else:
                    redirect_url= '/homeMedico'
                status_code = 303

            else:
                req.session["error"] = "Erro ao cadastrar. Tente novamente."
                req.session["errorStatus"] = True
            
    except pymysql.MySQLError as e:

        print(e)

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
        redirect_url = "/login"
        status_code = 303

    finally:
        db.close()
    
    print(redirect_url)
    print(status_code)

    return RedirectResponse(url=redirect_url, status_code=status_code)

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

            cursor.execute("SELECT * FROM Usuario WHERE Email = %s", (Login))
            user = cursor.fetchone()

            if user:
                if verify_password(SenhaLogin, user[7]):

                    req.session["nome_usuario"] = user[3] 
                    req.session["sobrenome_usuario"] = user[4] 
                    req.session["email_usuario"] = user[2] 
                    req.session["numero_usuario"] = user[6] 
                    req.session["cpf_usuario"] = user[1] 
                    req.session["data_usuario"] = user[5].strftime('%Y-%m-%d') 
                    req.session["ID_usuario"] = user[0]
                    req.session["papel"] = user[9]
                    req.session["foto_usuario"] = f"/usuario/foto/{user[2]}"
                else:
                    req.session["errorLogin"] = "Senha inválida."
                    req.session["errorLoginStatus"] = True
                    return RedirectResponse(url="/login", status_code=303)

            else:
                req.session["errorLogin"] = "Usuário inválido."
                req.session["errorLoginStatus"] = True
                return RedirectResponse(url="/login", status_code=303)
            
    except pymysql.MySQLError as e:
        print(e)
    finally:
        db.close()
    
    access_token = create_access_token(user[2])
    req.session["access_token"] = access_token
    req.session["token_type"] = 'bearer'

    if user[9] == 2:
        return RedirectResponse(url="/homeMedico", status_code=303)
    else:
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

            sql_delete = "DELETE FROM Consulta WHERE ID_paciente = %s"
            cursor.execute(sql_delete, (ID_Usuario,))
            db.commit()

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
    ID_Usuario: str = Form(...),
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
            req.session["ID_usuario"] = ID_Usuario
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