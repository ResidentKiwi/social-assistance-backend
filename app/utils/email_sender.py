import httpx
import os

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = "contato@meuportalsocial.site"  # Seu domínio verificado no Resend

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
            "html": f"""
                <div style="font-family: sans-serif; font-size: 16px; color: #333;">
                    <p>Olá,</p>
                    <p>Seu código de verificação é:</p>
                    <p style="font-size: 24px; font-weight: bold; color: #5c6bc0;">{code}</p>
                    <p>O código expira em 15 minutos.</p>
                    <p>— Equipe Portal de Apoio Social</p>
                </div>
            """
        }
    )

    if not (200 <= response.status_code < 300):
        raise Exception(f"Erro ao enviar e-mail: {response.status_code} {response.text}")
