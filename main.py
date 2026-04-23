from urllib import response

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests
import os
import json
from datetime import datetime

from database import Session, Boleto
from ocr import ocr_image, ocr_pdf
from parser import parsear_boleto

from twilio.twiml.messaging_response import MessagingResponse

from requests.auth import HTTPBasicAuth


app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

def converter_data_iso(data_str):
    try:
        return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except:
        return data_str


def processar_boleto(path):
    # OCR
    if path.endswith(".pdf"):
        texto = ocr_pdf(path)
    else:
        texto = ocr_image(path)
    resultado = parsear_boleto(texto)

    try:
        if isinstance(resultado, str):
            data = json.loads(resultado)
        else:
            data = resultado

        data["data_de_vencimento"] = converter_data_iso(data.get("data_de_vencimento", ""))
        data["data_do_documento"] = converter_data_iso(data.get("data_do_documento", ""))

        # salvar
        session = Session()
        boleto = Boleto(**data)
        session.add(boleto)
        session.commit()

        return data

    except Exception as e:
        print("ERRO:", e)
        return None

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    path = f"temp_{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    data = processar_boleto(path)

    os.remove(path)

    if not data:
        return {"erro": "Falha ao processar boleto"}

    return data


# =========================
# 📲 WEBHOOK WHATSAPP
# =========================

@app.post("/webhook")
async def whatsapp_webhook(
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None)
):
    resp = MessagingResponse()

    if NumMedia > 0 and MediaUrl0:
        print("📥 Recebido do WhatsApp:", MediaUrl0)

        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")

        response = requests.get(MediaUrl0,auth=HTTPBasicAuth(TWILIO_SID, TWILIO_TOKEN))

        print("STATUS:", response.status_code)
        
        filename = "whatsapp_boleto.jpg"

        with open(filename, "wb") as f:
            f.write(response.content)

        data = processar_boleto(filename)

        os.remove(filename)
  
    else:
            resp.message("Envie uma imagem de boleto 📸") 

    return str(resp)

@app.get("/boletos")
def listar_boletos():
    session = Session()

    boletos = session.query(Boleto).all()

    return [
        {
            "id": b.id,
            "linha_digitavel": b.linha_digitavel,
            "valor": b.valor,
            "data_do_documento": b.data_do_documento,
            "data_de_vencimento": b.data_de_vencimento,
            "beneficiario": b.beneficiario,
        }
        for b in boletos
    ]

@app.delete("/boletos/{boleto_id}")
def deletar_boleto(boleto_id: int):
    session = Session()
    boleto = session.query(Boleto).filter(Boleto.id == boleto_id).first()

    if not boleto:
        return {"erro": "Não encontrado"}

    session.delete(boleto)
    session.commit()

    return {"status": "ok"}


# =========================
# ✏️ EDITAR
# =========================

@app.put("/boletos/{boleto_id}")
def editar_boleto(boleto_id: int, data: dict):
    session = Session()
    boleto = session.query(Boleto).filter(Boleto.id == boleto_id).first()

    if not boleto:
        return {"erro": "Não encontrado"}

    boleto.linha_digitavel = data.get("linha_digitavel", boleto.linha_digitavel)
    boleto.valor = data.get("valor", boleto.valor)
    boleto.data_do_documento = data.get("data_do_documento", boleto.data_do_documento)
    boleto.data_de_vencimento = data.get("data_de_vencimento", boleto.data_de_vencimento)
    boleto.beneficiario = data.get("beneficiario", boleto.beneficiario)

    session.commit()

    return {"status": "ok"}