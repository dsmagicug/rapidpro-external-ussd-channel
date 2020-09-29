import json
import requests
import time
import secrets

HEADERS = requests.utils.default_headers()
HEADERS.update(
    {
        'Content-type': 'application/json',

    }
)
contacts = [
    "0772348900",
    "0773567654",
    "0755678789",
    "0789234354",
    "0773786734"
]
url = "http://127.0.0.1:8000/adaptor/call-back"

for i in range(3):
    contact = secrets.choice(contacts)

    payload = {
        "ussdRequestString": "Wrote you a letter, didn't wanna see you eyes, gonna hold onto my feelings no matter "
                             "who is wrong or right",
        "msisdn": "256772363256",
        "ussdServiceCode": "255",
        "transactionId": 2788574857454+i
    }
    req = requests.post(url, json.dumps(payload), headers=HEADERS)
    if req.status_code == 200:
        print(req.content)
    else:
        print(f"Error code {req.status_code}")
# while True:
#     req = requests.post(url, json.dumps(payload), headers=HEADERS)
#     if req.status_code == 200:
#         print(req.content)
#         sleep(0.01)
#     else:
#         raise Exception("Something is wrong")
