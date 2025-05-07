import os

"""
===============================================================================

Checks .stdout output files in a specified directory for known error messages 
from automated Prolific QC jobs.

Functionality:
- Scans all `.stdout` files in the target directory.
- Sorts files by most recent modification time.
- Searches for specified error strings (e.g., failed API calls).
- Returns a list of files containing at least one of the error messages.

Intended Use:
- Monitor SLURM job outputs for failures related to participant group updates.
- Can be used in daily QA routines or integrated into monitoring pipelines.

Parameters:
- `directory_path`: Directory where .stdout files are stored.
- `error_messages`: List of error message substrings to search for.

Returns:
- Prints files with errors, or a message if no errors were found.

===============================================================================
"""


def check_files_for_errors(directory_path, error_messages):
    # Get all files in the directory
    files = [f for f in os.listdir(directory_path) if f.endswith('.stdout')]
    # Sort files by modification time, most recent first
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory_path, x)), reverse=True)
    
    # List to hold files with errors
    files_with_errors = []

    # Check each file for the specified error messages
    for file in files:
        file_path = os.path.join(directory_path, file)
        try:
            with open(file_path, 'r') as file_content:
                content = file_content.read()
                # Check if any of the error messages are in the file
                if any(error_message in content for error_message in error_messages):
                    files_with_errors.append(file)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    return files_with_errors

# Directory path
directory_path = r'L:/rsmith/wellbeing/tasks/QC/daily_jobs_output'
# Error messages to check for
error_messages = ["Failed to patch participant group", "Failed to get participant group"]

# Get files with errors
error_files = check_files_for_errors(directory_path, error_messages)
if error_files:
    print("Files containing errors:")
    for file in error_files:
        print(file)
else:
    print("No errors found in any files.")
