import sys, os, re, subprocess, requests, json
import pandas as pd

"""
===============================================================================
get_messages.py

Checks whether a specific participant received a message on Prolific after
a specified timestamp.

Features:
- Uses the Prolific v1 API to retrieve all messages sent to a user after a
  given datetime (via `created_after` parameter).
- Compares message timestamps to determine if any messages were sent after
  the specified time.
- Sets a flag (1 or 0) to indicate whether at least one message matched.

Parameters:
- `subject`: Prolific participant ID to search messages for
- `time`: ISO-formatted datetime string (e.g., '2024-04-15T10:00:00.000')
- `API_token`: Prolific API token (in this case, Claire's)

Returns:
- flag = 1 if any message was sent after the specified time
- flag = 0 otherwise

Note:
- Currently hardcoded for one subject and token
- Can be extended for batch checks or logging as needed
===============================================================================
"""


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

