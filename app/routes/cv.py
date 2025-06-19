from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO

router = APIRouter()

@router.post("/generate")
async def generate_cv(data: dict, request: Request):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 3*cm

    def titulo(texto):
        nonlocal y
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(2*cm, y, texto)
        y -= 0.5*cm
        pdf.line(2*cm, y, width - 2*cm, y)
        y -= 0.7*cm

    def bloco(label, conteudo):
        nonlocal y
        if conteudo:
            if label:
                pdf.setFont("Helvetica-Bold", 11)
                pdf.drawString(2*cm, y, label)
                y -= 0.4*cm
            pdf.setFont("Helvetica", 10)
            for linha in conteudo.split('\n'):
                if y < 2*cm:
                    pdf.showPage()
                    y = height - 3*cm
                pdf.drawString(2.3*cm, y, linha.strip())
                y -= 0.4*cm
            y -= 0.3*cm

    # Cabeçalho com dados pessoais
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(2*cm, y, data["nome"])
    y -= 0.8*cm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(2*cm, y, f"E-mail: {data['email']} | Telefone: {data['telefone']}")
    y -= 1.2*cm

    # Sessões com conteúdo
    titulo("Objetivo Profissional")
    bloco("", data["objetivo"])

    titulo("Formação Acadêmica")
    bloco("", data["formacao"])

    if data.get("experiencia"):
        titulo("Experiência Profissional")
        bloco("", data["experiencia"])

    if data.get("cursos"):
        titulo("Cursos e Qualificações")
        bloco("", data["cursos"])

    if data.get("extras"):
        titulo("Informações Adicionais")
        bloco("", data["extras"])

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type='application/pdf', headers={"Content-Disposition": "attachment; filename=curriculo.pdf"})
