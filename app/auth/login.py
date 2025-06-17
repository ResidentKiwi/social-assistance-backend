from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()

# Simulação de banco de dados em memória
users_db = {}

class LoginData(BaseModel):
    email: EmailStr
    name: str

@router.post("/login")
def login_user(data: LoginData):
    email = data.email
    name = data.name
    if email not in users_db:
        users_db[email] = {"name": name}
    return {"message": f"Login registrado para {name}", "email": email}
