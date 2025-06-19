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
    y = height - 2.5*cm

    def section_title(text):
        nonlocal y
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(2*cm, y, text)
        y -= 0.5*cm

    def write_block(label, content, spacing=0.4):
        nonlocal y
        if content:
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(2*cm, y, f"{label}:")
            y -= 0.35*cm
            pdf.setFont("Helvetica", 10)
            for line in content.strip().split("\n"):
                pdf.drawString(2.4*cm, y, line.strip())
                y -= spacing*cm
            y -= 0.3*cm

    # Cabeçalho com dados básicos
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(2*cm, y, data["nome"])
    y -= 0.5*cm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(2*cm, y, f"Email: {data['email']} | Telefone: {data['telefone']}")
    y -= 0.4*cm
    if data.get("cidade") or data.get("nascimento") or data.get("linkedin"):
        if data.get("cidade"):
            pdf.drawString(2*cm, y, f"Cidade/UF: {data['cidade']}")
            y -= 0.4*cm
        if data.get("nascimento"):
            pdf.drawString(2*cm, y, f"Data de nascimento: {data['nascimento']}")
            y -= 0.4*cm
        if data.get("linkedin"):
            pdf.drawString(2*cm, y, f"LinkedIn: {data['linkedin']}")
            y -= 0.4*cm
    y -= 0.5*cm

    # Blocos principais
    section_title("Objetivo Profissional")
    write_block("", data["objetivo"])

    section_title("Formação Acadêmica")
    write_block("", data["formacao"])

    if data.get("experiencia"):
        section_title("Experiência Profissional")
        write_block("", data["experiencia"])

    if data.get("cursos"):
        section_title("Cursos e Qualificações")
        write_block("", data["cursos"])

    if data.get("extras"):
        section_title("Informações Adicionais")
        write_block("", data["extras"])

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type='application/pdf', headers={
        "Content-Disposition": "attachment; filename=curriculo.pdf"
    })
