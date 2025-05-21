import os
import shutil
from datetime import timedelta

from modules.guide import grab, merge
from modules.connection import is_connected
from modules.last_run import has_run_recently, update_last_run

# Set constants
HOST = "1.1.1.1"

CONFIG_PATH = "config"
GUIDE_PATH = "data"

RECENT_THRESHOLD = timedelta(minutes=30)

# Get environment variables
GUIDE_FILENAME = os.getenv("GUIDE_FILENAME", "guide-kr")
BACKUP_COUNT = int(os.getenv("BACKUP_COUNT", "7"))
RESTART_TIME = os.getenv("RESTART_TIME", "00:00")
FUTURE_THRESHOLD = int(os.getenv("FUTURE_THRESHOLD", "3"))
HISTORY_THRESHOLD = int(os.getenv("HISTORY_THRESHOLD", "3"))

TARGET_FILE = os.path.join(GUIDE_PATH, f"{GUIDE_FILENAME}.xml")
TMP_FILE = os.path.join(CONFIG_PATH, f"{GUIDE_FILENAME}.tmp")
LAST_RUN_FILE = os.path.join(CONFIG_PATH, "last_run.txt")

def run():
    if has_run_recently(LAST_RUN_FILE, RECENT_THRESHOLD):
        print(f"Guide file is already being grabbed, or has been grabbed recently. No guide file will be created")
        exit(0)

    update_last_run(LAST_RUN_FILE)

    # Check if the file exists
    backup_file = ""
    if os.path.isfile(TARGET_FILE):
        print(f"Guide file '{TARGET_FILE}' already exists")

        # Find the next available backup number
        for i in range(1, BACKUP_COUNT + 1):
            max_number_width = len(str(BACKUP_COUNT))
            backup_file = os.path.join(CONFIG_PATH, f"{GUIDE_FILENAME}.bak{i:0{max_number_width}}")

            if not os.path.exists(backup_file):
                shutil.copyfile(TARGET_FILE, backup_file)
                print(f"Backup created at '{backup_file}'")
                
                # Remove the next backup file if it exists
                next_backup = os.path.join(CONFIG_PATH, f"{GUIDE_FILENAME}.bak{(i % BACKUP_COUNT) + 1:0{max_number_width}}")
                if os.path.isfile(next_backup):
                    os.remove(next_backup)
                    print(f"The maximum backup count ({BACKUP_COUNT}) has been reached, removed '{next_backup}'")
                break
    else:
        print(f"Guide file '{TARGET_FILE}' does not yet exist")

    if is_connected(HOST):
        grab(TMP_FILE, HISTORY_THRESHOLD, FUTURE_THRESHOLD)

        if backup_file:
            merge(backup_file, TMP_FILE, history_threshold=HISTORY_THRESHOLD)

        shutil.move(TMP_FILE, TARGET_FILE)
        
        print(f"Guide file created at '{TARGET_FILE}'")
    else:
        print("Error: Could not connect to the internet. No guide file was created")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Error: An error has occurred while running this program. It will now exit")
        print(e)

        os.remove(TMP_FILE)
        os.remove(LAST_RUN_FILE)

        exit(1)