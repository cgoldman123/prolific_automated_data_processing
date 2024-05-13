import sys, os, re, subprocess, requests, json
import pandas as pd

time="2024-04-15T10:00:00.000"
subject = '62d9e46fded6a6209a518499'
API_token = 'x-XU7x9xV8ej3HPSA3Z2F_d-H0GtyL4rgh7L3VxffxweH01vtbEZRDKdvDQKQFdUfuST5lAUbp1NK-Qhgmq5rITrGfooFrpw3DsP6jmCYGdOUXHOlEIndTQM' # Claire's token

params = {
    "user_id": subject, 
    "created_after": time,
    "study_id": "65d650fc6fa9e61dfa165fc5"
}
args = {
    "Authorization": f"Token {API_token}"
}
response = requests.get(f"https://api.prolific.com/api/v1/messages/", headers=args, params=params)
data=response.json()
flag=0

for i in range(len(data['results'])):
    if data['results'][i]['datetime_created'] > time:
        flag=1

