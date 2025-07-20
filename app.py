from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YMONEY_TOKEN = os.getenv("YMONEY_TOKEN")
YMONEY_WALLET = os.getenv("YMONEY_WALLET")
DOWNLOAD_LINK = "https://termit-downloads.onrender.com/TERMIT_SETUP.zip"

class PaymentData(BaseModel):
    label: str
    telegram: str

@app.post("/check_payment")
async def check_payment(data: PaymentData):
    headers = {
        "Authorization": f"Bearer {YMONEY_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = { "label": data.label }
    response = requests.post("https://yoomoney.ru/api/operation-history", headers=headers, data=params)
    result = response.json()

    if "operations" in result:
        for operation in result["operations"]:
            if operation.get("status") == "success" and operation.get("label") == data.label:
                text = f"✅ Оплата получена! Скачайте программное обеспечение TERMIT: {DOWNLOAD_LINK}"
                requests.get(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    params={ "chat_id": data.telegram, "text": text }
                )
                return { "status": "success", "message": "Оплата подтверждена и сообщение отправлено" }
    return { "status": "fail", "message": "Оплата не найдена" }
