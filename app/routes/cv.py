from fastapi import APIRouter, HTTPException
from fpdf import FPDF
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO

router = APIRouter()

class CVData(BaseModel):
    name: str
    email: str
    experience: str

@router.post("/generate")
def generate_cv(data: CVData):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt=f"Currículo - {data.name}", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Email: {data.email}", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt=f"Experiência:\n{data.experience}")

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=curriculo.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
