
import os
import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YMONEY_TOKEN = os.getenv("YMONEY_TOKEN")
YMONEY_WALLET = os.getenv("YMONEY_WALLET")
DOWNLOAD_LINK = "https://termit-downloads.onrender.com/TERMIT_SETUP.zip"

class PaymentData(BaseModel):
    label: str
    telegram: str

@app.post("/check_payment")
async def check_payment(data: PaymentData):
    # Проверка оплаты через ЮMoney
    headers = {
        "Authorization": f"Bearer {YMONEY_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "label": data.label
    }
    response = requests.post("https://yoomoney.ru/api/operation-history", headers=headers, data=params)
    result = response.json()

    if "operations" in result:
        for operation in result["operations"]:
            if operation.get("status") == "success" and operation.get("label") == data.label:
                # Успешная оплата — отправляем ссылку в Telegram
                text = f"✅ Оплата получена!\nСкачайте программное обеспечение TERMIT:\n{DOWNLOAD_LINK}"
                requests.get(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    params={
                        "chat_id": data.telegram,
                        "text": text
                    }
                )
                return {"status": "success", "message": "Оплата подтверждена и сообщение отправлено"}
    return {"status": "fail", "message": "Оплата не найдена"}
