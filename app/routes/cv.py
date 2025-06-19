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
    else:
        return gerar_pdf_classico(data)

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
            pdf.setFont("Helvetica", 10)
            for linha in value.split('\n'):
                pdf.drawString(2.3*cm, y, linha.strip())
                y -= 0.4*cm
            y -= 0.3*cm

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(2*cm, y, data["nome"])
    y -= 0.5*cm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(2*cm, y, f"Email: {data['email']} | Telefone: {data['telefone']}")
    y -= 0.5*cm

    # Infos adicionais
    info_linha = []
    if data.get("cidade"): info_linha.append(data["cidade"])
    if data.get("nascimento"): info_linha.append("Nascimento: " + data["nascimento"])
    if data.get("estado_civil"): info_linha.append("Estado civil: " + data["estado_civil"])
    if data.get("linkedin"): info_linha.append("LinkedIn: " + data["linkedin"])
    if info_linha:
        pdf.drawString(2*cm, y, " | ".join(info_linha))
        y -= 0.7*cm

    # Conteúdo
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
            pdf.setFont("Helvetica", 10)
            for linha in conteudo.split('\n'):
                pdf.drawString(2.4*cm, y, linha.strip())
                y -= 0.35*cm
            y -= 0.3*cm

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(2*cm, y, data["nome"])
    y -= 0.6*cm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(2*cm, y, f"Email: {data['email']} | Tel: {data['telefone']}")
    y -= 0.5*cm

    if data.get("cidade") or data.get("nascimento") or data.get("estado_civil"):
        pdf.drawString(2*cm, y, " - ".join(filter(None, [
            data.get("cidade"), f"Nasc.: {data.get('nascimento')}", data.get("estado_civil")
        ])))
        y -= 0.5*cm
    if data.get("linkedin"):
        pdf.drawString(2*cm, y, f"LinkedIn: {data['linkedin']}")
        y -= 0.5*cm

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
