import requests as rq
import uuid

API_USER = str(uuid.uuid4())
url = "https://sandbox.momodeveloper.mtn.com/v1_0/apiuser"
headers = {
    "X-Reference-Id": API_USER,
    "Ocp-Apim-Subscription-Key": "ec014b3a18d248ed94494ab3a332d293",
    "Content-Type": "application/json"
}
body = {
    "providerCallbackHost": "string",
}

response = rq.post(url, json=body, headers=headers)
print("Status:", response.status_code)
print("API User ID:", API_USER)