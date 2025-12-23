import json
import pandas as pd
import ast
import hashlib

with open("data/raw_jobs.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)
print("Raw data shape:", df.shape)

df = df.dropna(subset=["job_title"])

df["company"] = df["company"].fillna("Unknown")

df.loc[
    (df["source"] == "remoteok") &
    (df["location"].isna() | (df["location"] == "any")),
    "location"
] = "Remote"

def generate_job_id(row):
    base = f"{row['job_title']}_{row['company']}_{row['location']}_{row['source']}"
    return hashlib.md5(base.lower().encode()).hexdigest()

df["job_id"] = df.apply(generate_job_id, axis=1)

df = df.drop_duplicates(subset=["job_id"])

print("After deduplication:", df.shape)

def normalize_skills(x):
    if isinstance(x, list):
        return [s.lower().strip() for s in x if isinstance(s, str)]

    if isinstance(x, str):
        try:
            parsed = ast.literal_eval(x)
            if isinstance(parsed, list):
                return [s.lower().strip() for s in parsed]
        except:
            return []

    return []

df["skills"] = df["skills"].apply(normalize_skills)

def classify_experience(title):
    title = title.lower()

    if any(k in title for k in ["intern", "junior", "trainee", "entry"]):
        return "Entry-level"
    elif any(k in title for k in ["senior", "lead", "manager"]):
        return "Senior"
    else:
        return "Mid-level"

df["experience_level"] = df["job_title"].apply(classify_experience)

df["num_skills"] = df["skills"].apply(len)

invalid_titles = [
    "current openings",
    "careers",
    "jobs",
    "open positions",
    "residency"
]

df = df[~df["job_title"].str.lower().isin(invalid_titles)]
df = df[df["num_skills"] > 0]

df.to_csv("data/cleaned_jobs.csv", index=False)
print("Cleaned data saved:", df.shape)
