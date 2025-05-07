import requests, json, os, time,random
from check_questionnaires import check_questionnaires
from task_checks_cmg import task_checks
from prolific_participant_groups import add_to_participant_groups
from send_message import second_session_message
from followup_message import send_followup_message
import pandas as pd
from datetime import datetime, timedelta, timezone


"""
===============================================================================
prolific_api.py

Main orchestration script for automated participant management in Prolific-based
longitudinal studies. This script pulls Prolific submission data, runs quality
control checks on behavioral and survey data, approves eligible participants,
adds them to the appropriate group for the next session, and sends reminder
messages.

Functionality:
- Evaluates whether a participant should be approved based on:
  - Completion status and timestamp
  - Attention check pass/fail results
  - Behavioral QC flags from task performance
- Automatically approves participants via Prolific API
- Logs failures in `participant_mistakes.txt`
- Adds approved participants to the participant group for their next session
- Sends automated messages encouraging session continuation
- Includes handlers for multiple cohorts (USA, Japan, Asia, etc.) across rounds

Intended Usage:
This script can be executed manually or on a schedule (e.g., via SLURM).
By default, only a subset of cohorts are activated. To enable additional
cohorts, uncomment the corresponding function in the `functions` list at bottom.

Dependencies:
- Requires local file: `carter_prolific_api_token.txt`
- Depends on utility modules: check_questionnaires, task_checks_cmg,
  send_message, followup_message, prolific_participant_groups

Authors: Carter Goldman and Claire Lavalley
===============================================================================
"""



if os.name == "nt":
    root = 'L:'
elif os.name == "posix":
    root = '/media/labs'

# initialize global counter to track how many submissions have been approved,
# so that we do not approve (and advance to other sessions) more than __ submissions
# at once to avoid over-working the server
num_submissions_approved = 0

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

studies_usa_cb1_r2 = {
    1:('665a36125a0f3c3cb092f567','cooperation','',''),
    2:('6659f73d9faab34ab2381a20','social','6659e3d0271bc74e6841d273',''),
    3:('6659f9bfabab1518dad222a9','dating_and_ToM', '6659e3e2f7f959147c664784',''),
    4:('6659fa44f69c2ea78f5fe1b3','advice', '6659e3efdd39d2f11487698c',''),
    5:('6659fcbe99e85b0ec6bafce5','faces', '6659e3fb45ae71208d7f7ba3',''),
}

studies_usa_cb2_r2 = {
    1:('6659fe56761cd977cc800be8','cooperation','',''),
    2:('6659fecaa9388e7971e5080c','social','6659ff17384b160d2ec963bb',''),
    3:('6659ffb9c62d40dd7738c510','dating_and_ToM', '6659ff283b2af336e6b6d3ab',''),
    4:('665a0015b0a7c3c3080fa304','advice', '6659ff333031c46f7df9a7e5',''),
    5:('665a00a0d602bed25511a2f9','faces', '6659ff41566ce6a7ff2d5e97',''),
}

studies_asia_cb1_r1 = {
    1:('665f369edd629ea90acc81a6','faces','',''), # using corrected project ID
    2:('665a225d99b96e515e1e51aa','advice','665a2335abaffb1117c59cc8',''),
    3:('665a262961819c47de502de0','dating_and_ToM', '665a233efc18959d6c8f4a58',''),
    4:('665a2662aea810cb8ff4c844','social', '665a234af36150654ab32d83',''),
    5:('665a2697344945410389820a','cooperation', '665a23535f683f4d0ed647a8',''),
}

studies_asia_cb2_r1 = {
    1:('665f36149054be030ed517c0','faces','',''), # using correctted project ID
    2:('665a27b25cdab4876b2d6704','advice','665a238d07dc7c6c8f2f679d',''),
    3:('665a27e9f8a77b62563b0191','dating_and_ToM', '665a2398152454bb2e630630',''),
    4:('665a280ad5e0e7f47c7fdfe2','social', '665a23a0ecf98c5daa3cbc63',''),
    5:('665a2843c79e6bed8c56cb39','cooperation', '665a23aa57546a49a3fc9508',''),
}

studies_asia_cb1_r2 = {
    1:('665f365b20162e9ac943c233','cooperation','',''), # using corrected project ID
    2:('665a2ac14d8b38f6682d9ec6','social','665a23cd77c7b504ed7d125d',''),
    3:('665a2b01a74f01a774740cd6','dating_and_ToM', '665a23d8cec6848f16a00975',''),
    4:('665a2b376c9708bd900a9bec','advice', '665a24e9c20a6f66b592f59d',''),
    5:('665a2b679aa44d8ecbb1c4b4','faces', '665a24ff0f473bd47c34d578',''),
}

studies_asia_cb2_r2 = {
    1:('665a2ba01d10972d59422c0b','cooperation','',''),
    2:('665a2dad7630dc2ff040cdbb','social','665a2529640487f7dd2b2819',''),
    3:('665a2dde32a1b5618efbae8c','dating_and_ToM', '665a2546d5c023bf4776ee2a',''),
    4:('665a2e21a990540cf8be84fd','advice', '665a255257097d4fb5a00afa',''),
    5:('665a2e44a0698cd45b233d4c','faces', '665a255da0c87db18a2693f2',''),
}

studies_india_asia_cb1_r1 = {
    1:('667b377f6498bcdfed2de506','faces','',''),
    2:('667c7870f9b72e1f201dd541','advice','667c75af2f80e6b1aa65549a',''),
    3:('667c794f82b73b3e10cf771b','dating_and_ToM', '667c75c1792363f6f9f52f15',''),
    4:('667c7a10c0542aee42f6b81a','social', '667c75d3b413fd17bc3dae1c',''),
    5:('667c7a85fd000eb8eceb70a8','cooperation', '667c75e90f6292151ecfe4c5',''),
}

studies_india_asia_cb2_r1 = {
    1:('667b3818137db703824dd1c6','faces','',''),
    2:('667c7b1c827314cd6f700ca2','advice','667c76d58998f0dd0e8dbfa1',''),
    3:('667c7b8a3dc8ad0a4ad3f630','dating_and_ToM', '667c76eeb1594eb8fe7a75fc',''),
    4:('667c7be3afaacb4612f6bd9e','social', '667c76fb2bfdd774e9c50d74',''),
    5:('667c7cf7f9b72e1f201dd629','cooperation', '667c77093dc8ad0a4ad3f585',''),
}

studies_india_asia_cb1_r2 = {
    1:('667b370d0bd5a9f5831a7686','cooperation','',''),
    2:('667c7e39be456820ed7abb4f','social','667c761af22501407ef67bd8',''),
    3:('667c7e8056e786c5661ac022','dating_and_ToM', '667c765b6565ef685c5cdcfe',''),
    4:('667c7f010bdb83d9e32f522c','advice', '667c766d3cfbb8856d7b34f7',''),
    5:('667c7fa477e81cff2e7eed4e','faces', '667c767cd1c1166e79caa096',''),
}

studies_india_asia_cb2_r2 = {
    1:('667af739092af948c4fffe06','cooperation','',''),
    2:('667c803a360fe35909cae6b1','social','667c7744f77b3115bb7abc55',''),
    3:('667c8083b9ca760b999913e9','dating_and_ToM', '667c7752473a0d58a0a8de99',''),
    4:('667c80bdb743b050bcf6b8c4','advice', '667c7760e57a1c6f476e4302',''),
    5:('667c8100c0542aee42f6b968','faces', '667c776ff77b3115bb7abc5a',''),
}

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








# ------------------------------------------------------------------------------
# check_proj_subs(study, studies)
# 
# - Checks each participant submission for a given study session.
# - Approves those who pass all attention and behavioral QC checks.
# - Logs failed cases to participant_mistakes.txt.
# - Automatically adds approved participants to the next session's group.
# - Optionally sends a Session 2 message after completing Session 1.
#
# Arguments:
# - study: Session number (1–5)
# - studies: Dictionary mapping session to study metadata
# ------------------------------------------------------------------------------

def check_proj_subs(study,studies):
    global num_submissions_approved
    project_id = studies[study][0]
    project_name = studies[study][1]
    pt_group_update = []
    response = requests.get(f"https://api.prolific.com/api/v1/studies/{project_id}/submissions/?limit=500&offset=0", headers=headers)
    if response.ok:
        print(f"Submission information retrieved successfully for session {study}")
        submissions_data = response.json()

    else:
        print(f"Failed to get submission information for session {study}. Error: {response.status_code}")
        print(response.text)
        submissions_data = {}
        submissions_data['results'] = []

    for result in submissions_data['results']:
        # exit the loop if submission approve counter is greater than server limit
        if num_submissions_approved > 20:
            print("Have already approved more than 30 submissions, not approving any more to avoid overworking server")
            break
       
        # Check if the status is 'AWAITING REVIEW'
        if result['status'] == 'AWAITING REVIEW':
            subject = result['participant_id']
            try: 
                datetime_obj = datetime.strptime(result['completed_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
            except ValueError:
                datetime_obj = datetime.strptime(result['completed_at'], '%Y-%m-%dT%H:%M:%S%z')
            
            if datetime_obj >= datetime.now(timezone.utc)-timedelta(hours=18):
                continue

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
                if study != 5:
                    pt_group_update.append([studies[study+1][0],subject])
                    num_submissions_approved = num_submissions_approved +1
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
        if session_id in ["6616ad447bf1d2e9056df906", "6644d57076eb22dadb502204","664b5d0be46bae63ae071549","665733da63de0137bb9a86e7","6659f73d9faab34ab2381a20","6659fecaa9388e7971e5080c","665a225d99b96e515e1e51aa","665a27b25cdab4876b2d6704","665a2ac14d8b38f6682d9ec6","665a2dad7630dc2ff040cdbb"]:
            second_session_message(subject_id) 
    add_to_participant_groups(ids_by_session, study+1, studies)
        












# ------------------------------------------------------------------------------
# Batch Execution
#
# - A list of cohort-check functions is defined (currently only Asian Nationals).
# - The list is shuffled to avoid hitting the same study order each run.
# - Each function is called sequentially.
#
# To enable additional cohorts, uncomment them in the `functions` list.
# This allows flexible control over which participant groups are processed.
# ------------------------------------------------------------------------------




# def check_usa_cb1():
#     print("\nChecking USA CB1!")
#     for study in studies_usa:
#         check_proj_subs(study,studies_usa)
#         if study != 1:
#             send_followup_message(study, studies_usa[study][0], studies_usa[study][2])

# def check_usa_cb2():
#     print("\nChecking USA CB2!")
#     for study in studies_usa_cb2:
#         check_proj_subs(study,studies_usa_cb2)
#         if study != 1:
#             send_followup_message(study, studies_usa_cb2[study][0], studies_usa_cb2[study][2])

# def check_japan_cb1():
#     print("\nChecking Japan CB1!")
#     for study in studies_japan:
#         check_proj_subs(study,studies_japan)
#         if study != 1:
#             send_followup_message(study, studies_japan[study][0], studies_japan[study][2])

# def check_japanese_cb1():
#     print("\nChecking Japanese CB1!")
#     for study in studies_japanese:
#         check_proj_subs(study,studies_japanese)
#         if study != 1:
#             send_followup_message(study, studies_japanese[study][0], studies_japanese[study][2])

# def check_usa_cb1_r2():
#     print("\nChecking USA R2 CB1!")
#     for study in studies_usa_cb1_r2:
#         check_proj_subs(study,studies_usa_cb1_r2)
#         if study != 1:
#             send_followup_message(study, studies_usa_cb1_r2[study][0], studies_usa_cb1_r2[study][2])

# def check_usa_cb2_r2():
#     print("\nChecking USA CB2 R2!")
#     for study in studies_usa_cb2_r2:
#         check_proj_subs(study,studies_usa_cb2_r2)
#         if study != 1:
#             send_followup_message(study, studies_usa_cb2_r2[study][0], studies_usa_cb2_r2[study][2])

# def check_asia_cb1_r1():
#     print("\nChecking Asia CB1 R1!")
#     for study in studies_asia_cb1_r1:
#         check_proj_subs(study,studies_asia_cb1_r1)
#         if study != 1:
#             send_followup_message(study, studies_asia_cb1_r1[study][0], studies_asia_cb1_r1[study][2])

# def check_asia_cb2_r1():
#     print("\nChecking Asia CB2 R1!")
#     for study in studies_asia_cb2_r1:
#         check_proj_subs(study,studies_asia_cb2_r1)
#         if study != 1:
#             send_followup_message(study, studies_asia_cb2_r1[study][0], studies_asia_cb2_r1[study][2])

# def check_asia_cb1_r2():
#     print("\nChecking Asia CB1 R2!")
#     for study in studies_asia_cb1_r2:
#         check_proj_subs(study,studies_asia_cb1_r2)
#         if study != 1:
#             send_followup_message(study, studies_asia_cb1_r2[study][0], studies_asia_cb1_r2[study][2])

# def check_asia_cb2_r2():
#     print("\nChecking Asia CB2 R2!")
#     for study in studies_asia_cb2_r2:
#         check_proj_subs(study,studies_asia_cb2_r2)
#         if study != 1:
            # send_followup_message(study, studies_asia_cb2_r2[study][0], studies_asia_cb2_r2[study][2])

# def check_india_asia_cb1_r1():
#     print("\nChecking INDIA/ASIA R1 CB1!")
#     for study in studies_india_asia_cb1_r1:
#         check_proj_subs(study,studies_india_asia_cb1_r1)
#         if study != 1:
#             send_followup_message(study, studies_india_asia_cb1_r1[study][0], studies_india_asia_cb1_r1[study][2])

# def check_india_asia_cb2_r1():
#     print("\nChecking INDIA/ASIA R1 CB2!")
#     for study in studies_india_asia_cb2_r1:
#         check_proj_subs(study,studies_india_asia_cb2_r1)
#         if study != 1:
#             send_followup_message(study, studies_india_asia_cb2_r1[study][0], studies_india_asia_cb2_r1[study][2])

# def check_india_asia_cb1_r2():
#     print("\nChecking INDIA/ASIA R2 CB1!")
#     for study in studies_india_asia_cb1_r2:
#         check_proj_subs(study,studies_india_asia_cb1_r2)
#         if study != 1:
#             send_followup_message(study, studies_india_asia_cb1_r2[study][0], studies_india_asia_cb1_r2[study][2])

# def check_india_asia_cb2_r2():
#     print("\nChecking INDIA/ASIA R2 CB2!")
#     for study in studies_india_asia_cb2_r2:
#         check_proj_subs(study,studies_india_asia_cb2_r2)
#         if study != 1:
#             send_followup_message(study, studies_india_asia_cb2_r2[study][0], studies_india_asia_cb2_r2[study][2])

def check_asian_nationals_cb1_r1():
    print("\nChecking ASIAN NATIONALS R1 CB1!")
    for study in studies_asian_nationals_cb1_r1:
        check_proj_subs(study,studies_asian_nationals_cb1_r1)
        if study != 1:
            send_followup_message(study, studies_asian_nationals_cb1_r1[study][0], studies_asian_nationals_cb1_r1[study][2])

def check_asian_nationals_cb2_r1():
    print("\nChecking ASIAN NATIONALS R1 CB2!")
    for study in studies_asian_nationals_cb2_r1:
        check_proj_subs(study,studies_asian_nationals_cb2_r1)
        if study != 1:
            send_followup_message(study, studies_asian_nationals_cb2_r1[study][0], studies_asian_nationals_cb2_r1[study][2])
            

def check_asian_nationals_cb1_r2():
    print("\nChecking ASIAN NATIONALS R2 CB1!")
    for study in studies_asian_nationals_cb1_r2:
        check_proj_subs(study,studies_asian_nationals_cb1_r2)
        if study != 1:
            send_followup_message(study, studies_asian_nationals_cb1_r2[study][0], studies_asian_nationals_cb1_r2[study][2])

def check_asian_nationals_cb2_r2():
    print("\nChecking ASIAN NATIONALS R2 CB2!")
    for study in studies_asian_nationals_cb2_r2:
        check_proj_subs(study,studies_asian_nationals_cb2_r2)
        if study != 1:
            send_followup_message(study, studies_asian_nationals_cb2_r2[study][0], studies_asian_nationals_cb2_r2[study][2])
            






# List of functions
functions = [
    # check_usa_cb1,
    #  check_usa_cb2,
    # check_japan_cb1,
    # check_japanese_cb1,
    # check_usa_cb1_r2,
    # check_usa_cb2_r2,
    # check_asia_cb1_r1,
    # check_asia_cb2_r1,
    # check_asia_cb1_r2,
    # check_asia_cb2_r2
    # check_india_asia_cb1_r1,
    # check_india_asia_cb2_r1,
    # check_india_asia_cb1_r2,
    # check_india_asia_cb2_r2,
    check_asian_nationals_cb1_r1,
    check_asian_nationals_cb2_r1,
    check_asian_nationals_cb1_r2,
    check_asian_nationals_cb2_r2,
]

# Shuffle the list of functions
random.shuffle(functions)

# Execute each function in the shuffled list
for func in functions:
    func()