from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class BenefitData(BaseModel):
    name: str
    age: int
    income: float

@router.post("/check")
def check_benefits(data: BenefitData):
    result = []

    if data.income < 1500:
        result.append("Possível elegibilidade para Auxílio Brasil")
    if data.age < 24:
        result.append("Possível acesso a programas educacionais")
    if not result:
        result.append("Nenhum benefício identificado com os dados informados")

    return {"recommendations": result}
