from pprint import pprint
from smsaero import SmsAero, SmsAeroException


SMSAERO_EMAIL = 'p.v.zagornyak@gmail.com'
SMSAERO_API_KEY = 'JAK37p5LPHZyqp5eCQOLZve3E4PlAHTj'


def send_sms(phone: int, message: str) -> dict:
    api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
    return api.send_sms(phone, message)

if __name__ == '__main__':
    try:
        result = send_sms(79110039433, 'Hello, World!')
        pprint(result)
    except SmsAeroException as e:
        print(f"An error occurred: {e}")