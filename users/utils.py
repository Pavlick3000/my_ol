from pprint import pprint
from smsaero import SmsAero, SmsAeroException


SMSAERO_EMAIL = 'p.v.zagornyak@gmail.com'
SMSAERO_API_KEY = 'JAK37p5LPHZyqp5eCQOLZve3E4PlAHTj'


def send_sms(phone_number: int, message: str) -> dict:

    phone_number = int(phone_number)  # Преобразуем в целое число
    api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
    return api.send_sms(phone_number, message)

