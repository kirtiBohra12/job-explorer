import pandas as pd
import streamlit as st
import ast
from collections import Counter
from datetime import datetime

st.set_page_config(page_title="Job Explorer Dashboard", layout="wide")

st.markdown("""
<style>
/* Sidebar accent color (blue) */
section[data-testid="stSidebar"] {
    border-right: 2px solid #2563eb;
}

/* KPI card text */
.kpi-title {
    color: #e5e7eb;
    font-size: 14px;
    margin-bottom: 4px;
}

.kpi-value {
    color: #ffffff;
    font-size: 22px;
    font-weight: 700;
    margin: 0;
}

/* KPI card container */
.kpi-card {
    background-color: #374151;
    padding: 8px 10px;
    border-radius: 8px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache
def load_data():
    return pd.read_csv("data/cleaned_jobs.csv")

# --- Tech Skills Whitelist ---
TECH_SKILL_WHITELIST = {
    "python", "java", "c", "c++", "c#", "go", "golang", "php",
    "javascript", "typescript", "node", "node.js", "ruby",
    "sql", "mysql", "postgresql", "postgres", "redis", "elasticsearch", "excel",
    "react", "angular", "laravel", "graphql",
    "aws", "azure", "gcp", "docker", "kubernetes", "devops",
    "linux", "api", "microservices",
    "git", "github",
    "ai", "ml", "machine learning"
}

# --- Extract Top Tech Skills ---
def extract_tech_skills(data):
    all_skills = []
    for skills in data["skills"].dropna():
        try:
            skill_list = ast.literal_eval(skills)
            for skill in skill_list:
                skill_clean = skill.lower().strip()
                if skill_clean in TECH_SKILL_WHITELIST:
                    all_skills.append(skill_clean)
        except:
            continue
    return Counter(all_skills)

# --- KPI Card ---
def kpi_card(title, value, icon):
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{icon} {title}</div>
            <div class="kpi-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def compute_freshness(df):
    if "fetched_at" not in df.columns:
        return "Unknown"

    df["fetched_at"] = pd.to_datetime(df["fetched_at"], errors="coerce")
    latest_time = df["fetched_at"].max()

    if pd.isna(latest_time):
        return "Unknown"

    now_utc = datetime.utcnow()
    hours_ago = int((now_utc - latest_time).total_seconds() / 3600)
    return f"{hours_ago} hrs ago"

def search_skills(skills_str, query):
    try:
        skills_list = ast.literal_eval(skills_str)
        skills_joined = " ".join([s.lower() for s in skills_list])
        return query.lower() in skills_joined
    except:
        return False

def main():
    data = load_data()

    st.sidebar.header("🎛️ Filters")

    selected_experience = st.sidebar.multiselect(
        "Experience Level",
        options=sorted(data["experience_level"].dropna().unique()),
        default=sorted(data["experience_level"].dropna().unique())
    )

    selected_location = st.sidebar.selectbox(
        "Select Location",
        options=["All"] + sorted(data["location"].dropna().unique())
    )

    filtered_data = data[
        data["experience_level"].isin(selected_experience)
    ]

    if selected_location != "All":
        filtered_data = filtered_data[filtered_data["location"] == selected_location]

    st.title("🤖 Job Explorer Dashboard")
    st.subheader("Explore jobs, roles & in-demand skills")

    left_col, right_col = st.columns([7, 3])

    with left_col:
        st.header("🔍 Explore Jobs")
        st.write("Search jobs by role, skill, or keyword")

        search_input = st.text_input(
            "Search",
            placeholder="e.g. python, data analyst, aws"
        )

        if search_input:
            search_results = filtered_data[
                filtered_data["job_title"].str.contains(
                    search_input, case=False, na=False, regex=False
                ) |
                filtered_data["skills"].str.contains(
                    search_input, case=False, na=False, regex=False
                )
            ]
        else:
            search_results = filtered_data

        st.write(f"💼 Showing **{len(search_results)} jobs**")

        for _, row in search_results.iterrows():
            st.markdown(f"### {row['job_title']}")
            st.write(f"🏢 Company: {row['company']}")
            st.write(f"📍 Location: {row['location']}")
            st.write(f"🎓 Experience: {row['experience_level']}")
            st.markdown(f"🔗 [Apply Here]({row['url']})")
            st.markdown("---")

    with right_col:

        tech_skill_counter = extract_tech_skills(filtered_data)

        freshness = compute_freshness(filtered_data)

        kpi_card("Total Jobs", len(filtered_data), "📌")
        kpi_card("Data Freshness", freshness, "🕒")

        st.markdown("---")
        st.subheader("🔥 Top 10 Tech Skills")

        tech_skill_counter = extract_tech_skills(filtered_data)

        if len(tech_skill_counter) == 0:
            st.caption(
                "ℹ️ No tech skills found for selected filters — showing overall top skills."
            )
            tech_skill_counter = extract_tech_skills(data)

        if len(tech_skill_counter) > 0:
            top_skills = tech_skill_counter.most_common(10)

            chart_df = pd.DataFrame(
                {"Job Count": [count for _, count in top_skills]},
                index=[skill for skill, _ in top_skills]
            )

            st.bar_chart(chart_df)
        else:
            st.info("No skills available in the dataset.")


if __name__ == "__main__":
    main()
