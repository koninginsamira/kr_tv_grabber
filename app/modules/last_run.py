from datetime import datetime, timedelta
import os
from typing import Literal


def has_run_recently(last_run_file: str, threshold: timedelta):
    if os.path.exists(last_run_file):
        with open(last_run_file, "r") as file:
            time = datetime.fromisoformat(file.readline().strip())
            state = file.readline().strip()

        time_since_last_run = datetime.now() - time
        if state != "error" and time_since_last_run < threshold:
            return True
        
    return False


def update_last_run(last_run_file: str, state: Literal["started", "finished", "error"]):
    with open(last_run_file, "w") as file:
        file.writelines([
            datetime.now().isoformat() + "\n",
            state
        ])