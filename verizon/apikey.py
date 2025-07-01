import requests as rq
import uuid

API_USER = str(uuid.uuid4())

# Step 1: Create API User
create_user_url = "https://sandbox.momodeveloper.mtn.com/v1_0/apiuser"
create_user_headers = {
    "X-Reference-Id": API_USER,
    "Ocp-Apim-Subscription-Key": "ec014b3a18d248ed94494ab3a332d293",
    "Content-Type": "application/json"
}
body = {
    "providerCallbackHost": "string",
}

response = rq.post(create_user_url, json=body, headers=create_user_headers)
print("Create User Status:", response.status_code)
print("API User ID:", API_USER)

# Step 2: Generate API Key for the created user
apikey_url = f"https://sandbox.momodeveloper.mtn.com/v1_0/apiuser/{API_USER}/apikey"
apikey_headers = {
    "Ocp-Apim-Subscription-Key": "ec014b3a18d248ed94494ab3a332d293",
    "Content-Type": "application/json"
}

response = rq.post(apikey_url, headers=apikey_headers)
print("API Key Status:", response.status_code)
try:
    print("API Key:", response.json().get("apiKey"))
except Exception as e:
    print("Error getting API Key:", e)