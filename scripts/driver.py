#!/usr/bin/env python

import os
import subprocess
import sys
import datetime
import schedule
import time

# Constants
SCRIPTS_FOLDER = "../scripts"
LOGS_FOLDER = "../logs"

# Path to the log file
log_file = os.path.join(LOGS_FOLDER, "driver.log")

# Get the current date and time
current_time = datetime.datetime.now()

# Format the timestamp
timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

# Open the log file in append mode and write the timestamp
with open(log_file, "a") as file:
    file.write(f"Script execution started at {timestamp}\n")

def run_monitoring_script():
    monitor_script = os.path.join(SCRIPTS_FOLDER, "monitor.py")
    try:
        subprocess.run(["python3", monitor_script], check=True)
        print("Successfully ran monitor script")
        # Call the analyzer script after the monitor script has completed
        run_analyzer_script()

    except subprocess.CalledProcessError as e:
        print(f"Error running the monitor script: {e}")
        # Get the current date and time
        current_time = datetime.datetime.now()

        # Format the timestamp
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # Open the log file in append mode and write the timestamp
        with open(log_file, "a") as file:
            file.write(f"ERROR at {timestamp}: {e}\n")
        sys.exit(1)

def run_analyzer_script():
    analyzer_script = os.path.join(SCRIPTS_FOLDER, "analyzer.py")
    try:
        subprocess.run(["python3", analyzer_script], check=True)
        print("Successfully ran analyzer script")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running the analyzer script: {e}")
        # Get the current date and time
        current_time = datetime.datetime.now()

        # Format the timestamp
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # Open the log file in append mode and write the timestamp
        with open(log_file, "a") as file:
            file.write(f"ERROR at {timestamp}: {e}\n")
        sys.exit(1)

def main():
    # Schedule the script to run every 5 minutes
    schedule.every(5).minutes.do(run_monitoring_script)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
