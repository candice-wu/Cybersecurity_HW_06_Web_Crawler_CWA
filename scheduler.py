import schedule
import time
import subprocess
import datetime

def job():
    print(f"[{datetime.datetime.now()}] Starting scheduled data fetch...")
    try:
        # Run the fetch_data.py script
        # We use subprocess to run it as a separate process to ensure clean execution environment
        subprocess.run(["python", "fetch_data.py"], check=True)
        print(f"[{datetime.datetime.now()}] Data fetch completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.datetime.now()}] Error: fetch_data.py failed with exit code {e.returncode}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Unexpected error: {e}")

def main():
    print("Scheduler started. Will run data fetch every 1 hour.")
    print("Press Ctrl+C to stop.")
    
    # Run once immediately on startup
    job()
    
    # Schedule subsequent runs
    schedule.every(1).hours.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
