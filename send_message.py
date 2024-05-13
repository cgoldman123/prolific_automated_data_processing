import sys, os, re, subprocess, requests, json, random
import pandas as pd

sys.tracebacklimit=0

API_token_claire = 'x-XU7x9xV8ej3HPSA3Z2F_d-H0GtyL4rgh7L3VxffxweH01vtbEZRDKdvDQKQFdUfuST5lAUbp1NK-Qhgmq5rITrGfooFrpw3DsP6jmCYGdOUXHOlEIndTQM' # Claire's token
API_token_carter = "dxzxkNAQZi5afGugMGDASEGuIEhgYrFSX7pa90DuyZWjisRgkmX3LrFhVHgfIhkBEp5SVPJZwGT_9KTO_RKDwvM8xaavT0fdGdKJwgs13sgfo24AO4AAWJFY"

# 6605ec91ca7a1b0793731140 -- Carter's id

def second_session_message(subject):
    params_claire = {
        "user_id": "6605ebe0d03f1f6d294a9d68", # Claire's id
        "recipient_id": subject, #"6605ec91ca7a1b0793731140",
        "body": """Hello!
            We'd like to first thank you for recently completing Session 1 of the Emotion and Decision-Making Study.  
            We're happy to let you know you have now been approved to complete Session 2. To be able to make full use of your data, we're hoping each session will be completed between 1 and 2 days apart, so that all 5 sessions are completed within a two-week period.
            You will be approved to complete each session on the day following your completion of the previous session. Please don't hesitate to contact us if any issues arise.
            Thanks so much again for your willingness to participate!""",
        "study_id": "65d650fc6fa9e61dfa165fc5"
    }

    params_carter = {
        "user_id": "6605ec91ca7a1b0793731140", # Carter's id
        "recipient_id": subject, #"6605ec91ca7a1b0793731140",
        "body": """Hello!
            We'd like to first thank you for recently completing Session 1 of the Emotion and Decision-Making Study.  
            We're happy to let you know you have now been approved to complete Session 2. To be able to make full use of your data, we're hoping each session will be completed between 1 and 2 days apart, so that all 5 sessions are completed within a two-week period.
            You will be approved to complete each session on the day following your completion of the previous session. Please don't hesitate to contact us if any issues arise.
            Thanks so much again for your willingness to participate!""",
        "study_id": "65d650fc6fa9e61dfa165fc5"
    }

    random_num = random.randint(1,2)
    if random_num==1:
        params = params_carter
        API_token = API_token_carter
    else:
        params = params_claire
        API_token = API_token_claire

    args = {
        "Authorization": f"Token {API_token}"
    }
    response = requests.post(f"https://api.prolific.com/api/v1/messages/", headers=args, json=params)

    if response.ok:
        print(f'Message successfully sent to {subject}')
    else:
        print(f'Failed to send message to {subject} {response.status_code}')
        print(response.text)
        