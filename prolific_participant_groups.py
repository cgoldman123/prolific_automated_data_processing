import requests, json, os, time

token = "dxzxkNAQZi5afGugMGDASEGuIEhgYrFSX7pa90DuyZWjisRgkmX3LrFhVHgfIhkBEp5SVPJZwGT_9KTO_RKDwvM8xaavT0fdGdKJwgs13sgfo24AO4AAWJFY"
workspace_id = "65d650fc6fa9e61dfa165fc5"

session1study_id = "6616a502839152e36a068a6b"
session2study_id = "6616ad447bf1d2e9056df906"
session3study_id = "6616ad8288fe3363982de0f9"
session4study_id = "6616adbb109058fc7983755e"
session5study_id = "6616ade849aa93dd9575a50c"

session1group_id = "6616a61065aee611338b0986"
session2group_id = "6616a62c94ee081cf6c8f51d"
session3group_id = "6616a6632e30de86b9b4538e"
session4group_id = "6616a67bdd5257ab64013d26"
session5group_id = "6616a68b0d40ff613474ee76"

session_and_group = {
    session1study_id:(session1group_id,1),
    session2study_id:(session2group_id,2),
    session3study_id:(session3group_id,3),
    session4study_id:(session4group_id,4),
    session5study_id:(session5group_id,5),
}

headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

def add_to_participant_groups(participants_to_add):
    for session_id in participants_to_add:
        # get current participants
        response = requests.get(f"https://api.prolific.com/api/v1/participant-groups/{session_and_group[session_id][0]}/participants", headers=headers)
        if response.ok:
            print(f"Successfully got participant group for session {session_and_group[session_id][1]}")
        else:
            print(f"Failed to get participant group for session {session_and_group[session_id][1]}. Error: {response.status_code}")
            print(response.text)
            continue
        data = response.json()
        participant_ids = [participant["participant_id"] for participant in data["results"]]
        # add participants to the group
        updated_participant_ids = participant_ids + participants_to_add[session_id]
        # patch participant group
        params = {
            "participant_ids": updated_participant_ids
        }
        response = requests.patch(f"https://api.prolific.com/api/v1/participant-groups/{session_and_group[session_id][0]}/", headers=headers,json=params)
        if response.ok:
            print(f"Successfully patched participant group for session {session_and_group[session_id][1]}")
            print(f"The updated participant group for session {session_and_group[session_id][1]} is {updated_participant_ids}")
        else:
            print(f"Failed to patch participant group for session {session_and_group[session_id][1]}. Error: {response.status_code}")
            print(response.text)

# function for manually adding to participant groups
def print_participants_to_add(participants_to_add):
    for session, ids in participants_to_add.items():
        ids_str = ','.join(ids)  # Join the IDs with commas
        print(f"Add the following IDs to session {session}: {ids_str}")

# Test
# participants_to_add = {
#     session1study_id: ["56e8bf5a870a8e000b4a8d6e","5ecda7f6509c241275db7396","6510cd961db8436e29a29680"],
#     session2study_id: ["56e8bf5a870a8e000b4a8d6e","5ecda7f6509c241275db7396","6510cd961db8436e29a29680"],
#     session3study_id: ["56e8bf5a870a8e000b4a8d6e","5ecda7f6509c241275db7396","6510cd961db8436e29a29680"],
#     session4study_id: ["56e8bf5a870a8e000b4a8d6e","5ecda7f6509c241275db7396","6510cd961db8436e29a29680"],
#     session5study_id: ["56e8bf5a870a8e000b4a8d6e","5ecda7f6509c241275db7396","6510cd961db8436e29a29680"]
# }

# add_to_participant_groups(participants_to_add)
