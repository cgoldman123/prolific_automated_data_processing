import requests, json, os, time

with open('carter_prolific_api_token.txt', 'r') as file:
    carter_api_token = file.read().strip()

workspace_id = "65d650fc6fa9e61dfa165fc5"


headers = {
    "Authorization": f"Token {carter_api_token}",
    "Content-Type": "application/json"
}

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

# function for manually adding to participant groups
def print_participants_to_add(participants_to_add):
    for session, ids in participants_to_add.items():
        ids_str = ','.join(ids)  # Join the IDs with commas
        print(f"Add the following IDs to session {session}: {ids_str}")


