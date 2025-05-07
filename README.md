# 🧠 Prolific Automated Data Processing

This repository automates participant tracking, approval, behavioral and survey data validation, and participant communication for longitudinal studies conducted via [Prolific](https://www.prolific.com). It supports complex designs with multiple cohorts, conditions, and repeated sessions.

To run locally, activate the conda virtual environment "prolific_api_automation" in  C:\Users\CGoldman\AppData\Local\anaconda3\envs\prolific_api_automation

All necessary packages/package versions can be found in environment.yml
---

## 📂 Project Structure

| Script | Description |
|--------|-------------|
| `run_daily_prolific.ssub` | This script schedules the compute cluster to run prolific_api.py at regular intervals to automate data processing. |
| `prolific_api.py` | Master pipeline: runs QC checks and messaging, controls participant advancement, and updates participant groups. This script calls many of the other scripts listed below.|
| `bulk_approve.py` | Approves participants marked as "AWAITING REVIEW" if they're on the session's approval list. |
| `check_active.py` | Checks which participants are currently active (status: `ACTIVE`) in each session. |
| `check_remaining_participants_todo_session.py` | Identifies participants who completed Session 4 but never began Session 5. |
| `check_output_files_for_errors.py` | Scans `.stdout` logs for API or group-related errors. |
| `check_questionnaires.py` | Verifies that required questionnaires were completed and attention checks were passed. |
| `followup_message.py` | Sends reminders to participants who haven’t started the next session within 48 hours. |
| `get_messages.py` | Checks to see if we have sent messages to a participant previously. |

| `prolific_participant_groups.py` | Adds participants to the appropriate group in Prolific to unlock the next session. |
| `pull_demographics.py` | Downloads and aggregates demographic data from each session. |
| `send_message.py` | Sends messages (e.g., session reminders) to participants using Carter or Claire's Prolific account. |
| `task_checks_cmg.py` | Performs detailed QC checks on behavioral data for all five tasks (faces, advice, dating, social media, cooperation). |

---

## 🔐 Authentication

You must provide two files in your root directory:

```bash
carter_prolific_api_token.txt
claire_prolific_api_token.txt

## ⚙️ Requirements

- Python ≥ 3.7
- `pandas`
- `requests`
- `numpy`
- `scipy`

Install via:

```bash
pip install -r requirements.txt
