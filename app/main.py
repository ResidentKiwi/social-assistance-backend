from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import login, email_verification
from app.routes import cv, benefits, admin
app.include_router(admin.router, prefix="/admin")

app = FastAPI()

# CORS para frontend no GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # substitua por domínio GitHub Pages se quiser restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router, prefix="/auth")
app.include_router(email_verification.router, prefix="/auth")
app.include_router(cv.router, prefix="/cv")
app.include_router(benefits.router, prefix="/benefits")

@app.get("/")
def read_root():
    return {"message": "API do Portal de Apoio Social funcionando."}
