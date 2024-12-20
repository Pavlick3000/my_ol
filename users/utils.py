import os
from pprint import pprint
from smsaero import SmsAero, SmsAeroException
from dotenv import dotenv_values

from my_ol.settings import BASE_DIR

config = dotenv_values(os.path.join(BASE_DIR, '.env'))

SMSAERO_EMAIL = 'p.v.zagornyak@gmail.com'
SMSAERO_API_KEY = config['SMSAERO_API_KEY']

def send_sms(phone_number: int, message: str) -> dict:

    phone_number = int(phone_number)  # Преобразуем в целое число
    api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
    return api.send_sms(phone_number, message)

