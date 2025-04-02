# pip install --upgrade -r requirements.txt

from fastapi import FastAPI

app = FastApi()

@app.get('/')
def hello() -> str: 
    return "Hello world!"