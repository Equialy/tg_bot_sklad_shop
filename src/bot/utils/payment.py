import yookassa
import uuid

from yookassa import Payment

from src.config.config import setting

yookassa.Configuration.account_id = setting.payment.account_id_yookassa
yookassa.Configuration.secret_key = setting.payment.secret_key_yookassa

async def create(amount, telegram_id):
    id_key = str(uuid.uuid4())
    payment = Payment.create(
        {
            "amount": {"value": amount, "currency": "RUB"},
            "payment_method_data": {"type": "bank_card"},
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/createMailing_bot",
            },
            "capture": True,
            "metadata": {"chat_id": telegram_id},
            "desctiption": "Описание товара....",
        },id_key
    )
    return payment.confirmation.confirmation_url, payment.id

async def check_payment(payment_id):
    payment = yookassa.Payment.find_one(payment_id)
    if payment.status == "succeeded":
        return payment.metadata
    else:
        return False