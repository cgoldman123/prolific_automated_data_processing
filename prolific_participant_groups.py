import requests, json, os, time

# ------------------------------------------------------------------------------
# prolific_participant_groups.py
#
# This script contains functions for managing participant group assignments
# on Prolific via the Prolific API.
#
# Main Functions:
# - `add_to_participant_groups`: Automatically appends new participants to a
#    specified Prolific participant group for the next session in a study.
# - `print_participants_to_add`: Manually prints out participant IDs that
#    should be added to a session (useful for manual QA or fallback).
#
# Requires:
# - A local API token in `carter_prolific_api_token.txt`
# - Study metadata passed via the `studies` dictionary
# ------------------------------------------------------------------------------


with open('carter_prolific_api_token.txt', 'r') as file:
    carter_api_token = file.read().strip()

workspace_id = "65d650fc6fa9e61dfa165fc5"


headers = {
    "Authorization": f"Token {carter_api_token}",
    "Content-Type": "application/json"
}


# ------------------------------------------------------------------------------
# add_to_participant_groups(participants_to_add, study, studies)
#
# Adds participants to the correct participant group for the next session.
#
# Parameters:
# - participants_to_add: dict mapping session_id → list of participant_ids
# - study: the current session number (e.g., 1–4)
# - studies: dictionary mapping session number → (project_id, name, group_id, ...)
#
# Steps:
# 1. GET current participants in the next session’s group.
# 2. Combine with new participants, ensuring uniqueness.
# 3. PATCH updated group back to Prolific.
# ------------------------------------------------------------------------------


def add_to_participant_groups(participants_to_add, study, studies):
    for session_id in participants_to_add:
        # get current participants
        response = requests.get(f"https://api.prolific.com/api/v1/participant-groups/{studies[study][2]}/participants", headers=headers)
        if response.ok:
            print(f"Successfully got participant group for session {study}")
        else:
            print(f"Failed to get participant group for session {study}. Error: {response.status_code}")
            print(response.text)
            continue
        data = response.json()
        participant_ids = [participant["participant_id"] for participant in data["results"]]
        # add participants to the group
        updated_participant_ids = participant_ids + participants_to_add[session_id]

        # only take unique participant IDs
        updated_participant_ids = list(set(updated_participant_ids))

        # patch participant group
        params = {
            "participant_ids": updated_participant_ids
        }
        response = requests.patch(f"https://api.prolific.com/api/v1/participant-groups/{studies[study][2]}/", headers=headers,json=params)
        if response.ok:
            print(f"Successfully patched participant group for session {study}")
            print(f"The updated participant group for session {study} is {updated_participant_ids}")
        else:
            print(f"Failed to patch participant group for session {study}. Error: {response.status_code}")
            print(response.text)


# ------------------------------------------------------------------------------
# print_participants_to_add(participants_to_add)
#
# Prints the participant IDs that should be added to each session group.
# Useful for manual review if automated PATCH is skipped or fails.
#
# Example Output:
# Add the following IDs to session 3: abc123, def456, ghi789
# ------------------------------------------------------------------------------


# function for manually adding to participant groups
def print_participants_to_add(participants_to_add):
    for session, ids in participants_to_add.items():
        ids_str = ','.join(ids)  # Join the IDs with commas
        print(f"Add the following IDs to session {session}: {ids_str}")


