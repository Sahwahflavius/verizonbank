import requests
from requests.auth import HTTPBasicAuth
DISBURSMENT_SUBSCRIPTION_KEY = '90f5d0cceb204025adfb28452b05899b'
DISBURSMENT_USER_ID = 'c818d16b-7476-406c-858f-55df302c3493'
DISBURSMENT_API_KEY = '1fba2416f8e5487a8e50d61399c47f0d'

# Ensure you have the correct values for DISBURSMENT_USER_ID and DISBURSMENT_API_KEY
# If you don't have them, you need to create an API user and generate an API key    
url = "https://sandbox.momodeveloper.mtn.com/disbursement/token/"

headers = {
    "Ocp-Apim-Subscription-Key": DISBURSMENT_SUBSCRIPTION_KEY
}

response = requests.post(
    url,
    headers=headers,
    auth=HTTPBasicAuth(DISBURSMENT_USER_ID, DISBURSMENT_API_KEY),
    timeout=30  # seconds
)

print("Status code:", response.status_code)
print("Response text:", response.text)

if response.ok:
    try:
        access_token = response.json().get("access_token")
        print("Access Token:", access_token)
    except Exception as e:
        print("Failed to parse JSON:", e)
else:
    print("Failed to get access token.")