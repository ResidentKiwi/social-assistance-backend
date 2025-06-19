import httpx
import os

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = "onboarding@resend.dev"  # email verificado pela Resend

def send_verification_email(to_email: str, code: str):
    if not RESEND_API_KEY:
        raise Exception("Resend API key não configurada")

    response = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        json={
            "from": f"Portal Apoio <{SENDER_EMAIL}>",
            "to": [to_email],
            "subject": "Código de Verificação – Portal de Apoio Social",
            "html": f"<p>Seu código de verificação é: <strong>{code}</strong></p><p>Ele expira em 15 minutos.</p>"
        }
    )

    if not (200 <= response.status_code < 300):
        raise Exception(f"Erro ao enviar e-mail: {response.status_code} {response.text}")
