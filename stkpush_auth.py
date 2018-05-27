import base64

import requests
import json
from requests.auth import HTTPBasicAuth

consumer_key = "tIBQaeAYI1IuRmJI87wNMFVf4NaX3xfr"
consumer_secret = "3VuwiaGfTJGZInbD"
api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
request_response = json.loads(r.text)
access_token = request_response['access_token']

print("Access Token: %s" % access_token)

password_string = '174379bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c91920180411111120'
password = base64.urlsafe_b64encode(password_string.encode('UTF-8')).decode('ascii')

print("Password: %s" % password)

api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
headers = {"Authorization": "Bearer %s" % access_token}
request = {
    "BusinessShortCode": "174379",
    "Password": password,
    "Timestamp": "20180411111120",
    "TransactionType": "CustomerPayBillOnline",
    "Amount": "300",
    "PartyA": "254708374149",
    "PartyB": "174379",
    "PhoneNumber": "254704230735",
    "CallBackURL": "https://tiba.herokuapp.com/",
    "AccountReference": "Null",
    "TransactionDesc": "Null"
}

response = requests.post(api_url, json=request, headers=headers)
#
print(response.text)
