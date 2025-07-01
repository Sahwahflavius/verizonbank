import uuid, requests
from config import DISBURSMENT_SUBSCRIPTION_KEY, DISBURSMENT_USER_ID, DISBURSMENT_API_KEY, MTN_ENVIRONMENT
from requests.auth import HTTPBasicAuth
from flask import Flask

app = Flask(__name__)

def get_mtn_token():
    url = "https://sandbox.momodeveloper.mtn.com/collection/token/"
    headers = {"Ocp-Apim-Subscription-Key": DISBURSMENT_SUBSCRIPTION_KEY}
    auth = HTTPBasicAuth(DISBURSMENT_USER_ID, DISBURSMENT_API_KEY)
    res = requests.post(url, headers=headers, auth=auth)
    return res.json().get("access_token")

def mtn_request_to_pay(phone, amount):
    token = get_mtn_token()
    reference_id = str(uuid.uuid4())

    url = "https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Reference-Id": reference_id,
        "X-Target-Environment": MTN_ENVIRONMENT,
        "Ocp-Apim-Subscription-Key": DISBURSMENT_SUBSCRIPTION_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "amount": str(amount),
        "currency": "EUR",
        "externalId": "123456",
        "payer": {"partyIdType": "MSISDN", "partyId": phone},
        "payerMessage": "Deposit",
        "payeeNote": "Thank you"
    }

    res = requests.post(url, json=payload, headers=headers)
    return {"status": res.status_code, "ref": reference_id}
