import os
from datetime import timedelta

from classes.guide import Guide
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
        return

    update_last_run(LAST_RUN_FILE, "started")

    guide = Guide().of_path(TARGET_FILE)
    backup: Guide | None = None

    if guide.exists():
        print(f"[backup] Guide file \"{guide.path}\" already exists.")
        backup = guide.copy()

        for i in range(1, BACKUP_COUNT + 1):
            max_number_width = len(str(BACKUP_COUNT))
            backup_path = os.path.join(CONFIG_PATH, f"{guide.filename}.bak{i:0{max_number_width}}")

            if not os.path.exists(backup_path):
                backup.write(backup_path)

                for entry in backup.history:
                    print("[backup] " + entry)
                
                # Remove the next backup file if it exists
                next_backup_path = os.path.join(CONFIG_PATH, f"{guide.filename}.bak{(i % BACKUP_COUNT) + 1:0{max_number_width}}")
                if os.path.isfile(next_backup_path):
                    os.remove(next_backup_path)
                    print(f"[backup] The maximum backup count ({BACKUP_COUNT}) has been reached, \"{next_backup_path}\" has been removed.")
                
                break
    else:
        print(f"[backup] Guide file \"{TARGET_FILE}\" does not yet exist.")

    print("")

    if is_connected(HOST):
        guide.grab(HISTORY_THRESHOLD, FUTURE_THRESHOLD)

        if backup and backup.exists():
            guide.merge(backup, HISTORY_THRESHOLD)

        guide.write()
        
        for entry in guide.history:
            print("[guide] " + entry)

        update_last_run(LAST_RUN_FILE, "finished")
    else:
        print("Error: Could not connect to the internet. No guide file was created.")


if __name__ == "__main__":
    code = 1

    try:
        print("")
        run()
        code = 0
    except Exception as e:
        print("Error: An error has occurred while running this program. It will now exit.")
        print()
        print(e)

        update_last_run(LAST_RUN_FILE, "error")
    finally:
        print("")
        exit(code)
