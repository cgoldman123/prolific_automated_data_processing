import requests, json, os, time,random
import pandas as pd
from datetime import datetime, timedelta, timezone

"""
===============================================================================
check_remaining_participants_todo_session.py

Identifies participants who were approved to complete Session 5 but never began it.

This script:
- Queries Prolific’s API to retrieve all participants approved for Session 4.
- Retrieves all participants who have started (or attempted) Session 5.
- Calculates the difference to flag those who never started Session 5.
- Prints missing participants by cohort (Round x Counterbalance group).

Functions:
- get_approved_session_4: returns IDs of participants approved for Session 4.
- get_started_session_5: returns IDs of participants who started Session 5
  (including all non-NEW statuses).
- The main script compares the two sets for each cohort and prints results.

Usage:
- Run manually to audit incomplete progression through the longitudinal study.

Notes:
- Uses API token stored in `carter_prolific_api_token.txt`.
- Focused on the "Asian Nationals" cohorts for R1 and R2.
===============================================================================
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
studies_asian_nationals_cb1_r1 = {
    1:('668ea7ae26f0946019b0e811','faces','',''),
    2:('668eaef49f3768a43591b8a4','advice','668eaa4a71caf817fa3b3fac',''),
    3:('668eaff3301ca34da5b6f908','dating_and_ToM', '668eaa5d07f6464955528810',''),
    4:('668eb0d055b437f5f77ac978','social', '668eaac511066e6169120abe',''),
    5:('668eb1d543f4ae83946be1fb','cooperation', '668eaad5c9645747122fbd96',''),
}

studies_asian_nationals_cb2_r1 = {
    1:('668ea7bd9f3768a43591b6f6','faces','',''),
    2:('668eaf07fb6dae6a848f4830','advice','668eaae786377d4637f973d8',''),
    3:('668eaff802de761d3230e7e8','dating_and_ToM', '668eaaf004135438a04e6d27',''),
    4:('668eb0d3fdb8063a4f8f48a2','social', '668eaaf9bb2504334973aaab',''),
    5:('668eb1e09d8b346fe48d6951','cooperation', '668eab04b575d617485d4c1b',''),
}


studies_asian_nationals_cb1_r2 = {
    1:('668ea7d3f3ff48f672b67069','cooperation','',''),
    2:('668eaf11531a38e36e4808d1','social','668eab35845ef46a5289c8d5',''),
    3:('668eb0057b5506daaa86d11c','dating_and_ToM', '668eab4cf28c825eab080b4c',''),
    4:('668eb0d8758a6f7bfeb29ea0','advice', '668eab6dc22aab4cccc1c5a9',''),
    5:('668eb1e7cb8c30e7e7ae7188','faces', '668eab771d615e85cc0eb216',''),
}

studies_asian_nationals_cb2_r2 = {
    1:('668ea7d9ffeba26ff46adcba','cooperation','',''),
    2:('668eaf1d6f7a6a79a99b38d5','social','668eab8e1b59868cb5577371',''),
    3:('668eb00b577ef76d86411643','dating_and_ToM', '668eaba31411a6cf4ff9eee4',''),
    4:('668eb0dbcd281249f614aac3','advice', '668eabad4863d388f8c85ebf',''),
    5:('668eb1e9c866e012da64db71','faces', '668eabb70c35bd8c4bcfd56d',''),
}



def get_approved_session_4(studies):
    project_id = studies[4][0]
    response = requests.get(f"https://api.prolific.com/api/v1/studies/{project_id}/submissions/?limit=500&offset=0", headers=headers)
    if response.ok:
        #print(f"Submission information retrieved successfully for session {study}")
        submissions_data = response.json()

    else:
        print(f"Failed to get submission information for session 4. Error: {response.status_code}")
        print(response.text)
        submissions_data = {}
        submissions_data['results'] = []


    session_4_approved_ids = []
    for result in submissions_data['results']:
        # do
        if result['status'] == 'APPROVED':
            session_4_approved_ids.append(result['participant_id'])

    return session_4_approved_ids
            
def get_started_session_5(studies):
    project_id = studies[5][0]
    response = requests.get(f"https://api.prolific.com/api/v1/studies/{project_id}/submissions/?limit=500&offset=0", headers=headers)
    if response.ok:
        #print(f"Submission information retrieved successfully for session {study}")
        submissions_data = response.json()

    else:
        print(f"Failed to get submission information for session 5. Error: {response.status_code}")
        print(response.text)
        submissions_data = {}
        submissions_data['results'] = []


    session_5_started_ids = []
    for result in submissions_data['results']:
        # do
        if result['status'] == 'APPROVED' or result['status'] == 'ACTIVE' or result['status'] == 'TIMED-OUT' or result['status'] == 'AWAITING REVIEW'or result['status'] == 'RETURNED'or result['status'] == 'REJECTED':
            session_5_started_ids.append(result['participant_id'])

    return session_5_started_ids


approved_session_4 = get_approved_session_4(studies_asian_nationals_cb1_r1)
started_session_5 = get_started_session_5(studies_asian_nationals_cb1_r1)
approved_set = set(approved_session_4)
started_set = set(started_session_5)
difference = approved_set - started_set
difference_list = list(difference)
print("R1 CB1: These people were approved for session 4 but never started session 5:", difference_list)


approved_session_4 = get_approved_session_4(studies_asian_nationals_cb2_r1)
started_session_5 = get_started_session_5(studies_asian_nationals_cb2_r1)
approved_set = set(approved_session_4)
started_set = set(started_session_5)
difference = approved_set - started_set
difference_list = list(difference)
print("R1 CB2: These people were approved for session 4 but never started session 5:", difference_list)



approved_session_4 = get_approved_session_4(studies_asian_nationals_cb1_r2)
started_session_5 = get_started_session_5(studies_asian_nationals_cb1_r2)
approved_set = set(approved_session_4)
started_set = set(started_session_5)
difference = approved_set - started_set
difference_list = list(difference)
print("R2 CB1: These people were approved for session 4 but never started session 5:", difference_list)

approved_session_4 = get_approved_session_4(studies_asian_nationals_cb2_r2)
started_session_5 = get_started_session_5(studies_asian_nationals_cb2_r2)
approved_set = set(approved_session_4)
started_set = set(started_session_5)
difference = approved_set - started_set
difference_list = list(difference)
print("R2 CB2: These people were approved for session 4 but never started session 5:", difference_list)
