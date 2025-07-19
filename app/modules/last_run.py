from datetime import datetime, timedelta
import os
from typing import Literal


def has_run_recently(last_run_file: str, threshold: timedelta):
    if os.path.exists(last_run_file):
        with open(last_run_file, "r") as file:
            time = datetime.fromisoformat(file.readline().strip())
            state = file.readline().strip()

        match state:
            case "started":
                return True
            case "finished":
                time_since_last_run = datetime.now() - time
                return time_since_last_run < threshold
            case _:
                return False
        
    return False

def update_last_run(last_run_file: str, state: Literal["started", "finished", "error", "stopped"]):
    with open(last_run_file, "w") as file:
        file.writelines([
            datetime.now().isoformat() + "\n",
            state
        ])