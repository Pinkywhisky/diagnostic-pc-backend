from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
import smtplib
from email.message import EmailMessage

app = FastAPI()

API_KEY = os.getenv("API_KEY", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
MAIL_TO = os.getenv("MAIL_TO", "")

class DiagnosticPayload(BaseModel):
    computer_name: str
    username: str
    app_version: str
    report: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/api/diagnostic")
def receive_diagnostic(payload: DiagnosticPayload, x_api_key: str | None = Header(default=None)):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not SMTP_USER or not SMTP_PASS or not MAIL_TO:
        raise HTTPException(status_code=500, detail="SMTP configuration incomplete")

    subject = f"Diagnostic PC - {payload.computer_name} - version {payload.app_version}"
    body = (
        f"Nom du poste : {payload.computer_name}\n"
        f"Utilisateur  : {payload.username}\n"
        f"Version outil : {payload.app_version}\n\n"
        f"{payload.report}"
    )

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Mail send failed: {exc}")

    return {"success": True, "message": "Diagnostic reçu et mail envoyé"}