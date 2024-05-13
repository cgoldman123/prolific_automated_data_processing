import requests, json, os, time
from check_questionnaires import check_questionnaires
from task_checks_cmg import task_checks
from prolific_participant_groups import add_to_participant_groups
from send_message import second_session_message
from followup_message import send_followup_message

if os.name == "nt":
    root = 'L:'
elif os.name == "posix":
    root = '/media/labs'

token = "dxzxkNAQZi5afGugMGDASEGuIEhgYrFSX7pa90DuyZWjisRgkmX3LrFhVHgfIhkBEp5SVPJZwGT_9KTO_RKDwvM8xaavT0fdGdKJwgs13sgfo24AO4AAWJFY"
workspace_id = "65d650fc6fa9e61dfa165fc5"

headers = {
    "Authorization": f"Token {token}"
}

studies_usa = {
    1:('6616a502839152e36a068a6b','faces'),
    2:('6616ad447bf1d2e9056df906','advice'),
    3:('6616ad8288fe3363982de0f9','dating_and_ToM'),
    4:('6616adbb109058fc7983755e','social'),
    5:('6616ade849aa93dd9575a50c','cooperation'),
}

studies_japan = {
    1:('6638fff29189dc7a7b72b504','faces'),
    2:('6616ad447bf1d2e9056df906','advice'),
    3:('6616ad8288fe3363982de0f9','dating_and_ToM'),
    4:('6616adbb109058fc7983755e','social'),
    5:('6616ade849aa93dd9575a50c','cooperation'),
}

def check_proj_subs(study,studies):
    project_id,project_name = studies[study]
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

    for result in submissions_data['results']:
        # Check if the status is 'AWAITING REVIEW'
        if result['status'] == 'AWAITING REVIEW':
            subject = result['participant_id']
            print(f"{subject} is awaiting review for session {study}")
            passed_all_attention_checks, total_attention_checks = check_questionnaires(subject,[study])
            if project_name == "dating_and_ToM":
                dating_checks = task_checks(subject,"dating")
                tom_checks = task_checks(subject,"tom")
                behavioral_checks = dating_checks+tom_checks
                passed_all_behavioral_checks = behavioral_checks[0][0] and behavioral_checks[1][0]
            else:
                behavioral_checks = task_checks(subject,project_name)
                passed_all_behavioral_checks = behavioral_checks[0][0]
            if passed_all_attention_checks and passed_all_behavioral_checks:
                print(f"{subject} passed all attention and behavioral checks!")
                params = {"action": "APPROVE"}
                response = requests.post(f"https://api.prolific.com/api/v1/submissions/{result['id']}/transition/", headers=headers, json=params)
                if response.ok:
                    print(f"{subject} was successfully approved for session {study}")
                else:
                    print(f"Failed to approve {subject} for session {study}. Error: {response.status_code}")
                    print(response.text)
                # if not the last study, 
                if project_name != 'cooperation':
                    pt_group_update.append([studies[study+1][0],subject])
            else:
                message = f"{subject} did not pass all checks for session {study}!\n"
                if not passed_all_attention_checks:
                    failed_questionnaire_checks = ', '.join(key for key, value in total_attention_checks.items() if value is False)
                    message = message + f"{subject} failed {failed_questionnaire_checks}\n"
                if not passed_all_behavioral_checks:
                    for task in behavioral_checks:
                        failed_task_checks = ', '.join(check for check in task[1])
                        message = message + f"{subject} failed task checks: {failed_task_checks}\n"
                print(message)
                with open(f'{root}/rsmith/wellbeing/tasks/QC/participant_mistakes.txt', "a") as file:  # Open file in append mode
                    file.write(message + "\n")

    ids_by_session = {}
    for session_id, subject_id in pt_group_update:
        if session_id not in ids_by_session:
            ids_by_session[session_id] = []  # Initialize the list
        ids_by_session[session_id].append(subject_id)
       # send message after first session
        if session_id == "6616ad447bf1d2e9056df906":
            second_session_message(subject_id) 
    add_to_participant_groups(ids_by_session)


for study in studies_usa:
    check_proj_subs(study,studies_usa)
    if study != 1:
       send_followup_message(study)

for study in studies_japan:
    check_proj_subs(study,studies_japan)    
    if study != 1:
        send_followup_message(study)


