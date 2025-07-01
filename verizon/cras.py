import requests

url = "https://sandbox.momodeveloper.mtn.com/disbursement/v1/transfers"
headers = {
"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSMjU2In0.eyJjbGllbnRJZCI6IjY3ZThlMDUzLTk2MjItNGY4YS1iOTM3LTNiZTE4OTI0NTllMSIsImV4cGlyZXMiOiIyMDI1LTA2LTIwVDAwOjExOjM0Ljk5NSIsInNlc3Npb25JZCI6ImNlZTZjMzZkLTZlOTItNDBjMS05MTg4LWYzOWY5NjI5NGI4NyJ9.CejBw9QS9Zo6w4-ihH0JxwFgkkLJuUj320oUYtaXlo_RmPsl3cH7lerfwuqTW9fGV5j0mJPVpPL1Q4WszWK7EkvlwmTLxrw-JBsSuKq1FIjImKixbVyTtcamw76pEsdi2eZVqehtO4UdQL_aBEcK_wKzfppdXwLFcjUXyivpsTJNkwto7yBKAM53Ph0ycIgmNXBU6DpWWgVUpGZpwVSlo0Ehqq-DHwOEWiVvWHz4c7-hQYwj4YiYISSsXL-sMysBDLRi-C6l5f9U32nB6wj6fptzCXbKm-j_K581huVHsvWJjrZIL1G4EqCARfcp8EUIeZVzSZVF7_9_sWBu2uG5Cg",
    "Content-Type": "application/json"
}
data = {
    "currency": "NGN",
    "amount": 1000,
    "billing_name": "John Doe"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())