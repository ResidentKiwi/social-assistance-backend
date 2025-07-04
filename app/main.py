# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importação das rotas
from app.routes import auth, cv, benefits, admin

app = FastAPI()

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Substitua por domínio específico na produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas
app.include_router(auth.router)
app.include_router(cv.router, prefix="/cv")
app.include_router(benefits.router, prefix="/benefits")
app.include_router(admin.router, prefix="/admin")

@app.get("/")
def read_root():
    return {"message": "API do Portal de Apoio Social funcionando."}
