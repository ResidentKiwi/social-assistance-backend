from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

router = APIRouter()

@router.post("/generate")
async def generate_cv(data: dict, request: Request):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    def draw_title(text):
        nonlocal y
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, text)
        y -= 20
        pdf.setLineWidth(0.5)
        pdf.line(50, y, width - 50, y)
        y -= 20

    def draw_block(label, content):
        nonlocal y
        if content:
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, y, label)
            y -= 15
            pdf.setFont("Helvetica", 11)
            for line in content.strip().split("\n"):
                for subline in split_line(line, 100):
                    pdf.drawString(60, y, subline)
                    y -= 15
            y -= 10

    def split_line(text, max_chars):
        return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

    # Cabeçalho
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, data['nome'])
    y -= 20
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Email: {data['email']}   |   Telefone: {data['telefone']}")
    y -= 30

    # Blocos de conteúdo
    draw_title("Objetivo Profissional")
    draw_block("", data['objetivo'])

    draw_title("Formação Acadêmica")
    draw_block("", data['formacao'])

    draw_title("Experiência Profissional")
    draw_block("", data.get('experiencia', ''))

    draw_title("Cursos e Qualificações")
    draw_block("", data.get('cursos', ''))

    draw_title("Informações Complementares")
    draw_block("", data.get('extras', ''))

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type='application/pdf', headers={"Content-Disposition": "attachment; filename=curriculo.pdf"})
