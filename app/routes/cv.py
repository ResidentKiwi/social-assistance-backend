from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO

router = APIRouter()

@router.post("/generate")
async def generate_cv(data: dict, request: Request, modelo: str = 'modelo1'):
    if modelo == 'modelo2':
        return gerar_pdf_moderno(data)
    return gerar_pdf_classico(data)

# ==== UTILITÁRIOS ====

def draw_multiline(pdf, x, y, text, font="Helvetica", size=10, leading=0.4*cm):
    pdf.setFont(font, size)
    for line in text.split('\n'):
        pdf.drawString(x, y, line.strip())
        y -= leading
    return y

# ==== MODELO CLÁSSICO ====

def gerar_pdf_classico(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2.5*cm

    def section(title, value):
        nonlocal y
        if value:
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(2*cm, y, title)
            y -= 0.4*cm
            y = draw_multiline(pdf, 2.3*cm, y, value)
            y -= 0.3*cm

    # Cabeçalho
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(2*cm, y, data.get("nome", ""))
    y -= 0.5*cm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(2*cm, y, f"Email: {data.get('email', '')} | Telefone: {data.get('telefone', '')}")
    y -= 0.5*cm

    # Informações extras
    info = []
    if data.get("cidade"): info.append(data["cidade"])
    if data.get("nascimento"): info.append("Nascimento: " + data["nascimento"])
    if data.get("estado_civil"): info.append("Estado civil: " + data["estado_civil"])
    if data.get("linkedin"): info.append("LinkedIn: " + data["linkedin"])
    if info:
        pdf.drawString(2*cm, y, " | ".join(info))
        y -= 0.7*cm

    # Seções
    section("Objetivo", data.get("objetivo"))
    section("Formação Acadêmica", data.get("formacao"))
    section("Experiência Profissional", data.get("experiencia"))
    section("Cursos e Qualificações", data.get("cursos"))
    section("Pretensão Salarial", data.get("salario"))
    section("Informações Adicionais", data.get("extras"))
    section("CNH", data.get("cnh"))
    section("Disponibilidade", data.get("disponibilidade"))

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type='application/pdf', headers={
        "Content-Disposition": "attachment; filename=curriculo-classico.pdf"
    })

# ==== MODELO MODERNO ====

def gerar_pdf_moderno(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 3*cm

    def bloco(titulo, conteudo):
        nonlocal y
        if conteudo:
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(2*cm, y, titulo.upper())
            y -= 0.4*cm
            y = draw_multiline(pdf, 2.4*cm, y, conteudo, size=10, leading=0.35*cm)
            y -= 0.3*cm

    # Cabeçalho
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(2*cm, y, data.get("nome", ""))
    y -= 0.6*cm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(2*cm, y, f"Email: {data.get('email', '')} | Tel: {data.get('telefone', '')}")
    y -= 0.5*cm

    extras = []
    if data.get("cidade"): extras.append(data["cidade"])
    if data.get("nascimento"): extras.append("Nasc.: " + data["nascimento"])
    if data.get("estado_civil"): extras.append(data["estado_civil"])
    if extras:
        pdf.drawString(2*cm, y, " - ".join(extras))
        y -= 0.5*cm
    if data.get("linkedin"):
        pdf.drawString(2*cm, y, f"LinkedIn: {data['linkedin']}")
        y -= 0.5*cm

    # Blocos principais
    bloco("Objetivo", data.get("objetivo"))
    bloco("Formação", data.get("formacao"))
    bloco("Experiência", data.get("experiencia"))
    bloco("Cursos", data.get("cursos"))
    bloco("Pretensão Salarial", data.get("salario"))
    bloco("Informações Adicionais", data.get("extras"))
    bloco("CNH", data.get("cnh"))
    bloco("Disponibilidade", data.get("disponibilidade"))

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type='application/pdf', headers={
        "Content-Disposition": "attachment; filename=curriculo-moderno.pdf"
    })
