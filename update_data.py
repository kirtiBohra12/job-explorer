import pandas as pd
from datetime import datetime
import pytz

def scrape_jobs():
    df = pd.read_csv("data/cleaned_jobs.csv")
    
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    df["fetched_at"] = now_ist.strftime("%d-%m-%Y %H:%M")
    
    df.to_csv("data/cleaned_jobs.csv", index=False)
    print("CSV updated successfully.")

if __name__ == "__main__":
    scrape_jobs()
