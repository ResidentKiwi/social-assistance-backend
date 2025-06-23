from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.utils.db import SessionLocal
from app.models import User
import bcrypt

router = APIRouter()

class LoginData(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login_user(data: LoginData):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    if not bcrypt.checkpw(data.password.encode(), user.password_hash):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    # A implementação abaixo é um exemplo com JWT
    from app.utils.auth import create_access_token
    token = create_access_token({"sub": str(user.id), "is_admin": user.is_admin})
    return {
        "message": "Login bem‑sucedido",
        "access_token": token,
        "token_type": "bearer",
        "user": { "id": user.id, "email": user.email, "username": user.username, "name": user.name }
    }
