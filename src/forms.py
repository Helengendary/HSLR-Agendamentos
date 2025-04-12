from pydantic import BaseModel
from datetime import date

class UserForm(BaseModel):
    cpf: str
    email:str
    nome: str
    sobrenome: str
    dataNascimento: date
    telefone: str
    senha: str
