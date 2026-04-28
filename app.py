import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk

# -------------------
# USER DATABASE
# -------------------
users = {
    "admin": {"password": "1234", "role": "Coordinator"},
    "Mythri": {"password": "mythri@1234", "role": "Volunteer"},
    "Bhavya": {"password": "bhavya@2026", "role": "Coordinator"}
}

# -------------------
# CLEAN HEADERS HELPER
# -------------------
def clean_headers(df):
    # Strip spaces, remove "(Short answer)", and strip again
    df.columns = df.columns.str.strip().str.replace(r"\(.*\)", "", regex=True).str.strip()
    return df

# -------------------
# LOGIN FUNCTION
# -------------------
def login():
    st.title("Community Connect Dashboard")
    st.header("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.session_state["role"] = users[username]["role"]
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

# -------------------
# PROFILE PAGE
# -------------------
def profile():
    st.header("👤 Profile")
    sheet_url = "https://docs.google.com/spreadsheets/d/1nKcjFPzhCBWJPR8adLZ1wQWN9ImPQjWLydvWxTSWUSM/export?format=csv&gid=1348337901"
    try:
        volunteers = pd.read_csv(sheet_url)
        volunteers = clean_headers(volunteers)
        volunteers = volunteers.rename(columns={
            "Name": "Name",
            "Skill / Expertise": "Skill",
            "Location": "Location",
            "Availability": "Availability",
            "Contact Information": "Contact",
            "Matches": "Matches"
        })

        if "Name" in volunteers.columns:
            user_data = volunteers[volunteers["Name"] == st.session_state["user"]]
            if not user_data.empty:
                row = user_data.iloc[0]
                st.write(f"**Name:** {row['Name']}")
                st.write(f"**Skill:** {row['Skill']}")
                st.write(f"**Location:** {row['Location']}")
                st.write(f"**Availability:** {row['Availability']}")
                st.write(f"**Contact:** {row['Contact']}")
            else:
                st.warning("No exact profile found — showing all volunteers instead.")
                st.dataframe(volunteers)
    except Exception as e:
        st.error(f"Could not load volunteer data. Error: {e}")

# -------------------
# DASHBOARD PAGE
# -------------------
def dashboard():
    st.header("📊 Dashboard")
    sheet_url = "https://docs.google.com/spreadsheets/d/1vT7ra2p6TDuElpg0Ar7eWLD0g4tdHlO_p9Wir93g-Sw/export?format=csv&gid=22836738"
    try:
        needs = pd.read_csv(sheet_url)
        needs = clean_headers(needs)
        needs = needs.rename(columns={
            "NGO / Group Name": "NGO",
            "Type of Need": "Need_Type",
            "Location": "Location",
            "Urgency Level": "Urgency",
            "Description of Need": "Description",
            "Matches": "Matches"
        })

        if "NGO" in needs.columns:
            st.metric("Total NGOs", needs["NGO"].nunique())
            st.metric("Urgent Needs", (needs["Urgency"] == "High").sum())

            st.subheader("Needs by Category")
            needs_chart = alt.Chart(needs).mark_bar().encode(
                x="Need_Type",
                y="count()",
                color="Need_Type"
            )
            st.altair_chart(needs_chart, use_container_width=True)

            st.subheader("⚠️ Urgent Needs")
            urgent = needs[needs["Urgency"] == "High"]
            if not urgent.empty:
                for _, row in urgent.iterrows():
                    st.error(f"⚠️ {row['Need_Type']} need from {row['NGO']} at {row['Location']}")
        else:
            st.warning("Could not find NGO column — showing raw Needs table instead.")
            st.dataframe(needs)

    except Exception as e:
        st.error(f"Could not load community needs data. Error: {e}")

# -------------------
# MATCHES PAGE
# -------------------
def matches_page():
    st.header("🤝 Matches")
    sheet_url = "https://docs.google.com/spreadsheets/d/1nKcjFPzhCBWJPR8adLZ1wQWN9ImPQjWLydvWxTSWUSM/export?format=csv&gid=415150448"
    try:
        matches = pd.read_csv(sheet_url)
        matches = clean_headers(matches)
        matches = matches.rename(columns={
            "Need": "Need",
            "Need Title": "Need_Title",
            "Urgency": "Urgency",
            "Volunteer": "Volunteer",
            "Skill": "Skill",
            "Location": "Location",
            "Contact": "Contact"
        })

        if "Volunteer" in matches.columns:
            st.table(matches)

            st.subheader("Volunteers by Skill")
            skill_chart = alt.Chart(matches).mark_bar().encode(
                x="Skill",
                y="count()",
                color="Skill"
            )
            st.altair_chart(skill_chart, use_container_width=True)

            st.subheader("Volunteer Locations Map")
            demo_locations = pd.DataFrame({
                "lat": [17.3850, 17.4399],
                "lon": [78.4867, 78.4983],
                "Volunteer": ["Ravi Kumar", "Priya Sharma"]
            })
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=demo_locations,
                get_position='[lon, lat]',
                get_color='[0, 128, 255, 160]',
                get_radius=300,
                pickable=True
            )
            view_state = pdk.ViewState(latitude=17.4, longitude=78.48, zoom=10)
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "{Volunteer}"}
            ))
        else:
            st.warning("Could not find Volunteer column — showing raw Matches table instead.")
            st.dataframe(matches)

    except Exception as e:
        st.error(f"Could not load matches data. Error: {e}")

# -------------------
# SETTINGS PAGE
# -------------------
def settings():
    st.header("⚙️ Settings")
    st.info("Settings page is under construction.")

# -------------------
# MAIN APP FLOW
# -------------------
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    st.sidebar.title("🌐 Navigation")
    choice = st.sidebar.radio("Go to:", ["📊 Dashboard", "👤 Profile", "🤝 Matches", "⚙️ Settings"])
    if st.sidebar.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state["role"] = None
        st.success("You have been logged out. Please log in again.")
    if choice == "📊 Dashboard":
        dashboard()
    elif choice == "👤 Profile":
        profile()
    elif choice == "🤝 Matches":
        matches_page()
    elif choice == "⚙️ Settings":
        settings()
    st.markdown("<hr><center>© 2026 Community Connect</center>", unsafe_allow_html=True)
