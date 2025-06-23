from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

from app.utils.db import get_social_db
from app.models import Users

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        token = credentials.credentials if credentials else None
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.state.user = payload
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

async def admin_required(request: Request, db=Depends(get_social_db)):
    uid = request.state.user.get("sub")
    if not uid:
        raise HTTPException(status_code=400, detail="ID de usuário não encontrado no token.")
    
    user = db.query(Users).filter_by(id=uid).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")
    
    return True
