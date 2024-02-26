import base64
import requests
from datetime import datetime


def authorization(url, key, secret):
    plain_text = f'{key}:{secret}'
    bytes_obj = bytes(plain_text, 'utf-8')
    bs4 = base64.b64encode(bytes_obj)

    headers = {"Authorization": "Basic " + bs4.decode('utf-8')}

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res.json().get('access_token')
    except requests.RequestException as e:
        print(f"Error during access token retrieval: {e}")

        print(f"Response content: {res.text}")
        return None


def generate_timestamp():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    print(timestamp)
    return timestamp


def create_password(shortcode, passkey, timestamp):
    plain_text = f"{shortcode}{passkey}{timestamp}"
    bytes_obj = bytes(plain_text, 'utf-8')
    bs4 = base64.b64encode(bytes_obj)
    generated_password = bs4.decode('utf-8')
    print(f"Generated Password: {generated_password}")
    return generated_password


def make_deposit(number, key, secret):
    timestamp = generate_timestamp()
    token = authorization(
        "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials", key, secret)

    if token is not None:
        password = create_password(
            "174379", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919", timestamp)

        payload = {
            "BusinessShortCode": "174379",
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",
            "PartyA": number,
            "PartyB": "174379",
            "PhoneNumber": number,
            "CallBackURL": "https://mydomain.com/pat",
            "AccountReference": "Test",
            "TransactionDesc": "Test"
        }

        headers = {"Authorization": "Bearer " + token}

        try:
            res = requests.post(
                'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers=headers, json=payload
            )
            res.raise_for_status()
            print(res.json())
        except requests.RequestException as e:
            print(f"Error during payment processing: {e}")
    else:
        print("Failed to retrieve access token. Payment not processed.")


key = "SJFuEzKXob9ztiXh1nGKZCsAFT2BDbQmPGNpQOp95GKw7ASM"
secret = "AtQ9sa581NtvO8YB4E9m5VYsATlBLQSCAuG6ryr7slpApSgWe6ASrFuISxN1kxsg"

make_deposit("254720864496", key, secret)

result = authorization(
    "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials", key, secret)
print(result)
