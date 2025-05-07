import sys, os, requests, json, random, re
from datetime import datetime, timedelta

"""
===============================================================================
followup_message.py

Sends a follow-up message to participants who were added to a Prolific study 
participant group for Session X but have not started the session within 48 hours.

Workflow:
- For each participant in the group:
    1. Retrieves the time they were added to the participant group.
    2. Checks if they’ve already started a submission (any non-NEW status).
    3. Checks if they’ve received a relevant message from either Carter or Claire.
    4. If 48 hours have passed and none of the above apply, sends a reminder.

Message Logic:
- Participants are only contacted if:
    - 48 hours have passed since they were added.
    - They have NOT started the session.
    - They have NOT been messaged about this session.

Message Content:
- Encourages participants to continue within the 2-day window.
- Provides a gentle opt-out prompt and contact support.

API Authentication:
- Messages are randomly sent via Carter’s or Claire’s account to balance traffic.
- Uses API tokens stored in `carter_prolific_api_token.txt` and 
  `claire_prolific_api_token.txt`.

Inputs:
- session: Integer (1–5)
- study: Prolific study ID for that session
- id: Participant group ID for that session

Note:
- Output is printed to console (including dry-run message confirmations).
===============================================================================
"""


with open('carter_prolific_api_token.txt', 'r') as file:
    API_token_carter = file.read().strip()

with open('claire_prolific_api_token.txt', 'r') as file:
    API_token_claire = file.read().strip()

workspace_id = "65d650fc6fa9e61dfa165fc5"

headers_claire = {
    "Authorization": f"Token {API_token_claire}",
    "Content-Type": "application/json"
}
headers_carter = {
    "Authorization": f"Token {API_token_carter}",
    "Content-Type": "application/json"
}


# group_sessions = { # study id and then participant group
#     2:("6616ad447bf1d2e9056df906","6616a62c94ee081cf6c8f51d"),
#     3: ("6616ad8288fe3363982de0f9", "6616a6632e30de86b9b4538e"),
#     4: ("6616adbb109058fc7983755e", "6616a67bdd5257ab64013d26"),
#     5: ("6616ade849aa93dd9575a50c", "6616a68b0d40ff613474ee76")
# }

def send_followup_message(session, study, id):
    pts = requests.get(f"https://api.prolific.com/api/v1/participant-groups/{id}/participants/?limit=200&offset=0", headers=headers_claire)
    if pts.ok:
        print(f"Participant group successully gathered for {study}")
    else:
        print(f"Failed to get participant group for {study}. Error: {pts.status_code}")
    groupdata = pts.json()
    participant_ids = [participant["participant_id"] for participant in groupdata["results"]]
    groupdata = groupdata['results']

    subs = requests.get(f"https://api.prolific.com/api/v1/studies/{study}/submissions/?limit=200&offset=0", headers=headers_claire)
    if subs.ok:
        print(f"Submissions successully gathered for {study}")
    else:
        print(f"Failed to get submissions for {study}. Error: {subs.status_code}")
    submissions = subs.json()
    submission_ids = [participant["participant_id"] for participant in submissions["results"]]
    submissions = submissions['results']

    for item in range(len(groupdata)):
        tmp = groupdata[item]
        pid = tmp['participant_id']
        added_to_group = tmp['datetime_created']

        params = {
        "user_id": pid, 
        "created_after": added_to_group,
        "study_id": "65d650fc6fa9e61dfa165fc5"
        }

        messages_claire = requests.get(f"https://api.prolific.com/api/v1/messages/", headers=headers_claire, params=params)
        if messages_claire.ok:
            msgs_claire = messages_claire.json()    
        else:
            print("Messages were NOT successfully gotten for Claire")
            return   
        
        messages_carter = requests.get(f"https://api.prolific.com/api/v1/messages/", headers=headers_carter, params=params)
        if messages_carter.ok:
            msgs_carter = messages_carter.json()    
        else:
            print("Messages were NOT successfully gotten for Carter")
            return
        
        #initialize flag for hasn't started this session
        flag=[0]
        
        for i in range(len(msgs_claire['results'])):
            if (msgs_claire['results'][i]['datetime_created'] > added_to_group):
               flag.append(1)
            elif re.search('As you were approved', msgs_claire['results'][i]['body']):
                flag.append(1)

        for i in range(len(msgs_carter['results'])):
            if (msgs_carter['results'][i]['datetime_created'] > added_to_group):
                flag.append(1)   
            elif re.search('As you were approved', msgs_carter['results'][i]['body']):
                flag.append(1)           

        for sub in range(len(submissions)):
            stmp = submissions[sub]
            if stmp['participant_id'] == pid:
                # it's been less than 48 hours since they were added to the participant group for this session
                if '.' not in added_to_group:
                    added_to_group = added_to_group.replace('Z', '.000000Z')
                if datetime.strptime(added_to_group, '%Y-%m-%dT%H:%M:%S.%fZ')+timedelta(hours=48) > datetime.now():
                    flag.append(1)
                # they have started a submission in this session    
                elif stmp['participant_id']==pid and stmp['status'] in ['APPROVED', 'AWAITING REVIEW', 'ACTIVE', 'RETURNED', 'TIMED-OUT']:
                    flag.append(1)
        
        if sum(flag)==0 and datetime.strptime(added_to_group, '%Y-%m-%dT%H:%M:%S.%fZ')+timedelta(hours=48) < datetime.now():
            random_num = random.randint(1,2)
            if random_num==1:
                user_id = "6605ebe0d03f1f6d294a9d68"
                API_token = API_token_claire
            else:
                user_id = "6605ec91ca7a1b0793731140"
                API_token = API_token_carter
            
            params = {
            "user_id": user_id, 
            "recipient_id": pid,
            "body": """Hello! Thank you for your participation so far in our study.  
                To be able to make full use of your data, we're hoping each session will be completed within 2 days of the previous session, so that all 5 sessions are completed within a two-week period.
                As you were approved to begin the next session 2 days ago, we wanted to see if you are still willing and able to continue participating in our study. Please let us know if you can no longer continue and don't hesitate to contact us if any issues arise.""",
            "study_id": workspace_id
            }
            args = {
                "Authorization": f"Token {API_token}"
            }
            print(f"Message would have sent to {pid}")
            response = requests.post(f"https://api.prolific.com/api/v1/messages/", headers=args, json=params)

            if response.ok:
                print(f'Follow-up message successfully sent to {pid} about session {session}')
            else:
                print(f'Failed to send message to {pid} {response.status_code}')
                print(response.text)
