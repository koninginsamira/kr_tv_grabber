from datetime import datetime, timedelta
import os


def has_run_recently(last_run_file: str, recent_threshold: timedelta):
    if os.path.exists(last_run_file):
        with open(last_run_file, "r") as file:
            last_run_str = file.read().strip()

        last_run_time = datetime.fromisoformat(last_run_str)

        # Check if the last run time is within the threshold
        if datetime.now() - last_run_time < recent_threshold:
            return True
        
    return False

def update_last_run(last_run_file: str):
    with open(last_run_file, "w") as file:
        file.write(datetime.now().isoformat())