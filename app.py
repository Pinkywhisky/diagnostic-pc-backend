from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY", "changeme")

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
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Pour le moment on teste juste la réception
    print("=== DIAGNOSTIC RECU ===")
    print(payload.model_dump())

    return {"success": True, "message": "Diagnostic reçu"}