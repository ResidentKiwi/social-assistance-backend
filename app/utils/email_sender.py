import httpx
import os

RESEND_API_KEY = "re_Yebznayf_3QcLfq1hL6GUs8LPGfxG4bpx"

def send_verification_email(email: str, code: str):
    response = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        json={
            "from": "Portal Apoio <no-reply@meuportal.social>",
            "to": [email],
            "subject": "Código de verificação",
            "html": f"<p>Seu código de verificação é: <strong>{code}</strong></p>"
        }
    )
    if response.status_code != 200:
        raise Exception("Erro ao enviar e-mail")
