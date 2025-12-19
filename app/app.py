import os
from datetime import timedelta, datetime
import subprocess

from classes.notif import Notif
from modules.connection import is_connected
from modules.last_run import has_run_recently, update_last_run

# Set constants
HOST = "1.1.1.1"
CONFIG_PATH = "data"
LAST_RUN_THRESHOLD = timedelta(minutes=30)

# Get environment variables
FUTURE_THRESHOLD = int(os.getenv("FUTURE_THRESHOLD", "3"))
NOTIF_AGENTS = os.getenv("NOTIF_AGENTS", "").split(",")

GUIDE_FILENAME = os.getenv("GUIDE_FILENAME", "guide-kr")
TARGET_FILE = os.path.join(CONFIG_PATH, f"{GUIDE_FILENAME}.xml")
LAST_RUN_FILE = os.path.join(CONFIG_PATH, "last_run.txt")

def run(notif: Notif):
    start_time = datetime.now()

    if has_run_recently(LAST_RUN_FILE, LAST_RUN_THRESHOLD):
        msg = "Guide file is already being grabbed, or has been grabbed recently. No new guide file will be grabbed."
        print(msg)
        notif.notify(body=msg)
        return

    update_last_run(LAST_RUN_FILE, "started")

    if is_connected(HOST):
        subprocess.run([
            "npx",
            "-y", "tv_grab_kr",
            "--days", f"{FUTURE_THRESHOLD}",
            "--output", TARGET_FILE
        ], check=True)

        duration = datetime.now() - start_time
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = total_seconds % (60 * 60) // 60
        seconds = total_seconds % 60

        print("")
        print(f"Runtime: {hours}h {minutes}m {seconds}s.")

        notif.notify(
            title="A new guide was grabbed!",
            body=f"Runtime: {hours}h {minutes}m {seconds}s."
        )

        update_last_run(LAST_RUN_FILE, "finished")
    else:
        raise Exception("Error: Could not connect to the internet. No guide file was grabbed.")


if __name__ == "__main__":
    notif = Notif()
    for agent in NOTIF_AGENTS:
        notif.add(agent)

    try:
        print("")
        run(notif)
        print("")

        exit(0)
    except Exception as e:
        print("Error: An error has occurred while running this program. It will now exit.")
        print()
        print(e)
        print("")

        notif.notify(
            title="An error has occured while running this program!",
            body=f"{e}"
        )

        update_last_run(LAST_RUN_FILE, "error")

        exit(1)