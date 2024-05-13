import sys, os, requests, json
from datetime import datetime, timedelta,random


API_token_claire = 'x-XU7x9xV8ej3HPSA3Z2F_d-H0GtyL4rgh7L3VxffxweH01vtbEZRDKdvDQKQFdUfuST5lAUbp1NK-Qhgmq5rITrGfooFrpw3DsP6jmCYGdOUXHOlEIndTQM' # Claire's token
API_token_carter = "dxzxkNAQZi5afGugMGDASEGuIEhgYrFSX7pa90DuyZWjisRgkmX3LrFhVHgfIhkBEp5SVPJZwGT_9KTO_RKDwvM8xaavT0fdGdKJwgs13sgfo24AO4AAWJFY"


# 6605ec91ca7a1b0793731140 -- Carter's id
workspace_id = "65d650fc6fa9e61dfa165fc5"

headers_claire = {
    "Authorization": f"Token {API_token_claire}",
    "Content-Type": "application/json"
}
headers_carter = {
    "Authorization": f"Token {API_token_carter}",
    "Content-Type": "application/json"
}


group_sessions = { # study id and then participant group
    2:("6616ad447bf1d2e9056df906","6616a62c94ee081cf6c8f51d"),
    3: ("6616ad8288fe3363982de0f9", "6616a6632e30de86b9b4538e"),
    4: ("6616adbb109058fc7983755e", "6616a67bdd5257ab64013d26"),
    5: ("6616ade849aa93dd9575a50c", "6616a68b0d40ff613474ee76")
}

def send_followup_message(session):
    id = group_sessions[session][1]
    study = group_sessions[session][0]

    pts = requests.get(f"https://api.prolific.com/api/v1/participant-groups/{id}/participants/?limit=200&offset=0", headers=headers_claire)
    groupdata = pts.json()
    participant_ids = [participant["participant_id"] for participant in groupdata["results"]]
    groupdata = groupdata['results']

    subs = requests.get(f"https://api.prolific.com/api/v1/studies/{study}/submissions/?limit=200&offset=0", headers=headers_claire)
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
        msgs_claire = messages_claire.json()      
        
        messages_carter = requests.get(f"https://api.prolific.com/api/v1/messages/", headers=headers_carter, params=params)
        msgs_carter = messages_carter.json()      
        
        #initialize flag for hasn't started this session
        flag=[0]*(len(groupdata)+1)
        
        for i in range(len(msgs_claire['results'])):
            if (msgs_claire['results'][i]['datetime_created'] > added_to_group):
               flag[len(groupdata)]=1

        for i in range(len(msgs_carter['results'])):
            if (msgs_claire['results'][i]['datetime_created'] > added_to_group):
               flag[len(groupdata)]=1              

        for sub in range(len(submissions)):
            stmp = submissions[sub]
            if stmp['participant_id'] == pid:
                # it's been less than 48 hours since they were added to the participant group for this session
                if datetime.strptime(added_to_group, '%Y-%m-%dT%H:%M:%S.%fZ')+timedelta(hours=48) > datetime.now():
                    flag[sub]=1
                # they have started a submission in this session    
                elif stmp['participant_id']==pid and stmp['status'] in ['APPROVED', 'AWAITING REVIEW', 'ACTIVE', 'RETURNED', 'TIMED-OUT']:
                    flag[sub]=1
        
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

send_followup_message(5)