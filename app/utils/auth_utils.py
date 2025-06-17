from fastapi import Header, HTTPException
from app.utils.db import supabase

def admin_required(x_user_email: str = Header(...)):
    res = supabase.table("users").select("is_admin").eq("email", x_user_email).single().execute()
    if not res.data or not res.data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return True
