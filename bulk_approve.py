import requests, json, os, time
import pandas as pd

"""
================================================================================
approve_session_submissions.py

This script checks submissions for each session of several Prolific studies and 
automatically approves participants if:

1. Their submission is in 'AWAITING REVIEW' status.
2. Their participant ID appears in the pre-defined session 5 approval list.

Features:
- Works across multiple cultural cohorts (USA CB1/CB2, Japan CB1, Japanese CB1).
- Automatically loads the approval list from the path specified in the `studies` dictionary.
- Uses Prolific's v1 API to retrieve submissions and send approval requests.

Inputs:
- `studies_*` dictionaries define session structure: (project ID, name, group ID, approval list CSV path).
- API token is loaded from a local file (`carter_prolific_api_token.txt`).

Output:
- Prints approval actions to console and reports any failures with error messages.

Usage:
- Intended for routine batch approval of longitudinal study participants.
- Make sure the approve list CSV is up-to-date and correctly formatted with a 
  column named `participant_id`.

Notes:
- This script approves participants **only** if they were included in the approve list 
  for session 5 of the corresponding study.
- Encoding fallback (`utf-8` → `latin1`) is handled in case of character issues in CSV.

================================================================================
"""


if os.name == "nt":
    root = 'L:'
elif os.name == "posix":
    root = '/media/labs'

with open('carter_prolific_api_token.txt', 'r') as file:
    carter_api_token = file.read().strip()

workspace_id = "65d650fc6fa9e61dfa165fc5"

headers = {
    "Authorization": f"Token {carter_api_token}"
}

# dictionary contains session number: (session project ID, session name, session participant group ID, approve list file location)
studies_usa = {
    1:('6616a502839152e36a068a6b','faces','','./approve_lists/usa_approve_list_CB1/usa_approved_participants_session1_CB1.csv'),
    2:('6616ad447bf1d2e9056df906','advice','6616a62c94ee081cf6c8f51d','./approve_lists/usa_approve_list_CB1/usa_approved_participants_session2_CB1.csv'),
    3:('6616ad8288fe3363982de0f9','dating_and_ToM', '6616a6632e30de86b9b4538e','./approve_lists/usa_approve_list_CB1/usa_approved_participants_session3_CB1.csv'),
    4:('6616adbb109058fc7983755e','social', '6616a67bdd5257ab64013d26','./approve_lists/usa_approve_list_CB1/usa_approved_participants_session4_CB1.csv'),
    5:('6616ade849aa93dd9575a50c','cooperation', '6616a68b0d40ff613474ee76','./approve_lists/usa_approve_list_CB1/usa_approved_participants_session5_CB1.csv'),
}

studies_usa_cb2 = {
    1:('6644d500cd4ebdb4daf80c41','faces','','./approve_lists/usa_approve_list_CB2/usa_approved_participants_session1_CB2.csv'),
    2:('6644d57076eb22dadb502204','advice', '6644d89fc37c441dc3ebeada','./approve_lists/usa_approve_list_CB2/usa_approved_participants_session2_CB2.csv'),
    3:('6644d5ed2f2b5fe97122d37a','dating_and_ToM', '6644d8bb34bde12c5b47931d','./approve_lists/usa_approve_list_CB2/usa_approved_participants_session3_CB2.csv'),
    4:('6644d696dc67e4e407dca7d3','social', '6644d8de9268376a724f7cea','./approve_lists/usa_approve_list_CB2/usa_approved_participants_session4_CB2.csv'),
    5:('6644d7e233e81f8b16595896','cooperation', '6644d8fe8122109317c47f4b','./approve_lists/usa_approve_list_CB2/usa_approved_participants_session5_CB2.csv'),
}

studies_japan = {
    1:('6638fff29189dc7a7b72b504','faces','','./approve_lists/japan_approve_list_CB1/japan_approved_participants_session1_CB1.csv'),
    2:('664b5d0be46bae63ae071549','advice','6644f8e7a5e1622e5cf8fbc0','./approve_lists/japan_approve_list_CB1/japan_approved_participants_session2_CB1.csv'),
    3:('664b73cecce9861577829e90','dating_and_ToM', '6644f8f36f8e8cb0424a398f','./approve_lists/japan_approve_list_CB1/japan_approved_participants_session3_CB1.csv'),
    4:('664b74d8ce8bcfd0240d292a','social', '6644f905856dd858b521b3ca','./approve_lists/japan_approve_list_CB1/japan_approved_participants_session4_CB1.csv'),
    5:('664b75563199507f9ffced7b','cooperation', '6644f90f7ad90c49eff24542','./approve_lists/japan_approve_list_CB1/japan_approved_participants_session5_CB1.csv'),
}

studies_japanese = {
    1:('665649a6eb9a4519439281cd','faces','','./approve_lists/japanese_approve_list_CB1/japanese_approved_participants_session1_CB1.csv'),
    2:('665733da63de0137bb9a86e7','advice','66573308a1a5b0631cdd509b','./approve_lists/japanese_approve_list_CB1/japanese_approved_participants_session2_CB1.csv'),
    3:('665734cc660336b21d8e7213','dating_and_ToM', '66573316ff4736e46b398b74','./approve_lists/japanese_approve_list_CB1/japanese_approved_participants_session3_CB1.csv'),
    4:('665735477b759c5812413dcb','social', '6657339b7b3a31deecb07c03','./approve_lists/japanese_approve_list_CB1/japanese_approved_participants_session4_CB1.csv'),
    5:('665735ae1fbdc0b592ef912f','cooperation', '665733ac55e399bec6fe619c','./approve_lists/japanese_approve_list_CB1/japanese_approved_participants_session5_CB1.csv'),
}






def approv_proj_subs(study,studies):
    project_id = studies[study][0]
    project_name = studies[study][1]
    pt_group_update = []
    response = requests.get(f"https://api.prolific.com/api/v1/studies/{project_id}/submissions/?limit=200&offset=0", headers=headers)
    if response.ok:
        print(f"Submission information retrieved successfully for session {study}")
        submissions_data = response.json()

    else:
        print(f"Failed to get submission information for session {study}. Error: {response.status_code}")
        print(response.text)
        submissions_data = {}
        submissions_data['results'] = []

    # load in approve list
    try:
        approve_list_session5 = pd.read_csv(studies[5][3], encoding='utf-8')
    except UnicodeDecodeError:
        approve_list_session5 = pd.read_csv(studies[5][3], encoding='latin1')


    for result in submissions_data['results']:
        # Check if the status is 'AWAITING REVIEW'
        if result['status'] == 'AWAITING REVIEW' and (result['participant_id'] in approve_list_session5['participant_id'].values):
            subject = result['participant_id']
            print(f"{subject} should be approved for session {study}\n")
            params = {"action": "APPROVE"}
            response = requests.post(f"https://api.prolific.com/api/v1/submissions/{result['id']}/transition/", headers=headers, json=params)
            if response.ok:
                print(f"{subject} was successfully approved for session {study}")
            else:
                print(f"Failed to approve {subject} for session {study}. Error: {response.status_code}")
                print(response.text)

                

print("\nChecking USA CB1!")
for study in studies_usa:
    approv_proj_subs(study,studies_usa)

print("\nChecking USA CB2!")
for study in studies_usa_cb2:
    approv_proj_subs(study,studies_usa_cb2)    

print("\nChecking Japan CB1!")
for study in studies_japan:
    approv_proj_subs(study,studies_japan)    

print("\nChecking Japanese CB1!")
for study in studies_japanese:
    approv_proj_subs(study,studies_japanese)    
