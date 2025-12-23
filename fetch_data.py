import requests
import json
from datetime import datetime
import os

API_URL = "https://remoteok.com/api"

def fetch_jobs():
    response = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.json()

def filter_jobs(raw_data):
    jobs = []

    for item in raw_data:
        if not isinstance(item, dict):
            continue

        if "position" not in item or "tags" not in item:
            continue

        job = {
            "job_title": item.get("position"),
            "company": item.get("company"),
            "skills": item.get("tags"),
            "location": item.get("location"),
            "url": item.get("url"),
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "source": "remoteok"
        }

        jobs.append(job)

    return jobs

def fetch_arbeitnow_jobs():
    url = "https://www.arbeitnow.com/api/job-board-api"
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get("data", [])

def parse_arbeitnow_jobs(raw_jobs):
    jobs = []

    for item in raw_jobs:
        job = {
            "job_title": item.get("title"),
            "company": item.get("company_name"),

            "skills": [],

            "location": item.get("location"),
            "url": item.get("url"),
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "source": "arbeitnow"
        }

        jobs.append(job)

    return jobs

if __name__ == "__main__":

    NEW_JOBS = []

    # RemoteOK
    raw_remoteok = fetch_jobs()
    remoteok_jobs = filter_jobs(raw_remoteok)
    NEW_JOBS.extend(remoteok_jobs)

    # Arbeitnow
    raw_arbeitnow = fetch_arbeitnow_jobs()
    arbeitnow_jobs = parse_arbeitnow_jobs(raw_arbeitnow)
    NEW_JOBS.extend(arbeitnow_jobs)

    if os.path.exists("data/raw_jobs.json"):
        with open("data/raw_jobs.json") as f:
            OLD_JOBS = json.load(f)
    else:
        OLD_JOBS = []

    ALL_JOBS = OLD_JOBS + NEW_JOBS

    with open("data/raw_jobs.json", "w") as f:
        json.dump(ALL_JOBS, f, indent=2)

    print(
        f"Added {len(NEW_JOBS)} new jobs | "
        f"Total stored: {len(ALL_JOBS)}"
    )
