import uuid, requests
from config import ORANGE_CLIENT_ID, ORANGE_CLIENT_SECRET, ORANGE_MERCHANT_KEY
from requests.auth import HTTPBasicAuth

def get_orange_token():
    res = requests.post(
        "https://api.orange.com/oauth/v3/token",
        auth=HTTPBasicAuth(ORANGE_CLIENT_ID, ORANGE_CLIENT_SECRET),
        data={"grant_type": "client_credentials"}
    )
    return res.json().get("access_token")

def create_orange_payment(amount):
    token = get_orange_token()
    order_id = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "merchant_key": ORANGE_MERCHANT_KEY,
        "currency": "XAF",
        "order_id": order_id,
        "amount": str(amount),
        "return_url": "https://yourapp.com/success",
        "cancel_url": "https://yourapp.com/cancel",
        "notif_url": "https://yourapp.com/notify",
        "lang": "fr",
        "reference": "Deposit"
    }

    res = requests.post("https://api.orange.com/orange-money-webpay/cm/v1/webpayment", json=payload, headers=headers)
    return res.json()
