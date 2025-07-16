import os
from datetime import timedelta

from app.classes.guide import Guide
from modules.connection import is_connected
from modules.last_run import has_run_recently, update_last_run

# Set constants
HOST = "1.1.1.1"

CONFIG_PATH = "config"
GUIDE_PATH = "data"

LAST_RUN_THRESHOLD = timedelta(minutes=30)

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
    if has_run_recently(LAST_RUN_FILE, LAST_RUN_THRESHOLD):
        print(f"Guide file is already being grabbed, or has been grabbed recently. No new guide file will be created.")
        exit(0)

    update_last_run(LAST_RUN_FILE, "started")

    guide = Guide().of(TARGET_FILE)
    
    if guide.exists():
        print(f"Guide file \"{guide.path}\" already exists.")
        backup = guide.backup(BACKUP_COUNT)
        backup.write()
    else:
        print(f"Guide file \"{TARGET_FILE}\" does not yet exist.")

    print("")

    if is_connected(HOST):
        guide.grab(HISTORY_THRESHOLD, FUTURE_THRESHOLD)

        if backup and backup.exists():
            guide.merge(backup, HISTORY_THRESHOLD)

        guide.write()
        
        for entry in guide.history:
            print(entry)

        os.remove(TMP_FILE)

        update_last_run(LAST_RUN_FILE, "finished")
    else:
        print("Error: Could not connect to the internet. No guide file was created.")


if __name__ == "__main__":
    try:
        run()
        code = 0
    except Exception as e:
        print("Error: An error has occurred while running this program. It will now exit.")
        print()
        print(e)

        update_last_run(LAST_RUN_FILE, "error")

        code = 1
    finally:
        os.remove(TMP_FILE)
        exit(code)