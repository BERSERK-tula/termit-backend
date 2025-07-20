from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YMONEY_TOKEN = os.getenv("YMONEY_TOKEN")
YMONEY_WALLET = os.getenv("YMONEY_WALLET")
DOWNLOAD_LINK = "https://t.me/termit_files/5"
TELEGRAM_ADMIN_ID = os.getenv("CHAT_ID")


class PaymentCheck(BaseModel):
    telegram: str
    amount: float


@app.post("/confirm")
def confirm_payment(data: PaymentCheck):
    # Проверка оплаты в истории операций
    headers = {"Authorization": f"Bearer {YMONEY_TOKEN}"}
    response = requests.get("https://yoomoney.ru/api/operation-history", headers=headers)
    operations = response.json().get("operations", [])

    for op in operations:
        if op.get("direction") == "in" and op.get("status") == "success":
            if op.get("amount") >= data.amount and data.telegram.lower() in op.get("message", "").lower():
                # Отправка Telegram уведомления
                requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", params={
                    "chat_id": TELEGRAM_ADMIN_ID,
                    "text": f"💰 Оплата подтверждена от @{data.telegram} на сумму {op.get('amount')}₽"
                })
                return {"status": "success", "link": DOWNLOAD_LINK}

    return {"status": "fail", "reason": "Оплата не найдена"}
