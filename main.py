from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests, json, datetime

app = FastAPI()

# Загружаем конфиг
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

class Order(BaseModel):
    name: str
    address: str
    zipcode: str
    phone: str
    telegram: str
    payment_id: str

@app.post("/order")
def process_order(order: Order):
    # Проверка платежа
    headers = {"Authorization": f"Bearer {CONFIG['yoomoney_token']}"}
    res = requests.get("https://yoomoney.ru/api/operation-history", headers=headers)
    if res.status_code != 200:
        return {"status": "error", "message": "YooMoney API error"}

    found = False
    for op in res.json().get("operations", []):
        if op.get("operation_id") == order.payment_id and op.get("status") == "success":
            found = True
            break

    if not found:
        return {"status": "error", "message": "Payment not found"}

    # Отправка в Telegram
    msg = f"✅ Новый заказ:

👤 {order.name}
🏠 {order.address}, {order.zipcode}
📞 {order.phone}
✈️ @{order.telegram}"
    requests.get(f"https://api.telegram.org/bot{CONFIG['telegram_bot_token']}/sendMessage", params={
        "chat_id": CONFIG["telegram_admin_id"],
        "text": msg
    })

    # Запись в Google таблицу
    requests.get(CONFIG["google_apps_script_url"], params={
        "name": order.name,
        "address": order.address,
        "zipcode": order.zipcode,
        "phone": order.phone,
        "telegram": order.telegram
    })

    return {"status": "ok", "download_url": CONFIG["download_url"]}