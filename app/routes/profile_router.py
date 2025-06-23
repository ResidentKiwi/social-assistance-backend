from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.utils.db import get_social_db
from app.utils.auth_utils import JWTBearer, get_current_user
from app.models import User

router = APIRouter(prefix="/profile", dependencies=[Depends(JWTBearer())])

@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_social_db), user: User = Depends(get_current_user)):
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "Arquivo muito grande (máximo 5MB)")
    user.avatar = content
    db.commit()
    return {"message": "Avatar atualizado com sucesso."}

@router.get("/{user_id}/avatar")
def get_avatar(user_id: int, db: Session = Depends(get_social_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.avatar:
        raise HTTPException(404, "Avatar não encontrado")
    return Response(content=user.avatar, media_type="image/png")
