import streamlit as st
import sqlite3
import time
import random
from datetime import datetime, timedelta
import pandas as pd

from streamlit_geolocation import streamlit_geolocation
from streamlit_mic_recorder import speech_to_text


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SafeHer AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DATABASE
# =========================================================

DB_NAME = "safeher.db"


def db():
    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )


def init_db():

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            relationship TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger_type TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            email TEXT,
            pin TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================================================
# DATABASE HELPERS
# =========================================================

def add_contact(name, phone, relationship):

    conn = db()

    conn.execute(
        """
        INSERT INTO contacts
        (name, phone, relationship)
        VALUES (?, ?, ?)
        """,
        (name, phone, relationship)
    )

    conn.commit()
    conn.close()


def get_contacts():

    conn = db()

    result = conn.execute(
        """
        SELECT id, name, phone, relationship
        FROM contacts
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return result


def delete_contact(contact_id):

    conn = db()

    conn.execute(
        "DELETE FROM contacts WHERE id=?",
        (contact_id,)
    )

    conn.commit()
    conn.close()


def add_incident(
    trigger,
    description="",
    latitude=None,
    longitude=None,
    status="ACTIVE"
):

    conn = db()

    conn.execute(
        """
        INSERT INTO incidents
        (
            trigger_type,
            description,
            latitude,
            longitude,
            timestamp,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            trigger,
            description,
            latitude,
            longitude,
            datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
            status
        )
    )

    conn.commit()
    conn.close()


def get_incidents():

    conn = db()

    result = conn.execute(
        """
        SELECT
            id,
            trigger_type,
            description,
            latitude,
            longitude,
            timestamp,
            status
        FROM incidents
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return result


def save_profile(
    name,
    phone,
    email,
    pin
):

    conn = db()

    conn.execute(
        """
        INSERT OR REPLACE INTO profile
        (id, name, phone, email, pin)
        VALUES (1, ?, ?, ?, ?)
        """,
        (
            name,
            phone,
            email,
            pin
        )
    )

    conn.commit()
    conn.close()


def get_profile():

    conn = db()

    result = conn.execute(
        """
        SELECT name, phone, email, pin
        FROM profile
        WHERE id=1
        """
    ).fetchone()

    conn.close()

    return result


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "emergency_active": False,
    "latitude": None,
    "longitude": None,
    "safety_timer_end": None,
    "checkin_active": False,
    "checkin_destination": "",
    "checkin_deadline": None,
    "fake_call": False,
    "alarm_active": False,
    "safe_mode": False
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    text-align: center;
    font-size: 48px;
    font-weight: 800;
}

.subtitle {
    text-align: center;
    opacity: 0.7;
    margin-bottom: 25px;
}

.sos-card {
    padding: 30px;
    border-radius: 20px;
    border: 2px solid #ff4b4b;
    text-align: center;
}

.feature-card {
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #555;
    min-height: 130px;
}

.fake-call {
    padding: 40px;
    border-radius: 25px;
    text-align: center;
    border: 3px solid #555;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🛡️ SafeHer AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Intelligent Women Safety & Emergency Assistance System'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🛡️ SafeHer AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🆘 Emergency",
        "👥 Contacts",
        "📍 Live Location",
        "🎙️ AI Safety",
        "⏱️ Safety Timer",
        "🛡️ Safe Check-In",
        "📞 Fake Call",
        "📝 Incident Report",
        "📋 Incident History",
        "📊 Analytics",
        "👤 Profile",
        "⚙️ Settings"
    ]
)

st.sidebar.divider()

if st.session_state.emergency_active:

    st.sidebar.error(
        "🔴 EMERGENCY ACTIVE"
    )

else:

    st.sidebar.success(
        "🟢 SYSTEM SAFE"
    )


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.header("🏠 Safety Dashboard")

    contacts = get_contacts()
    incidents = get_incidents()

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        status = (
            "🔴 EMERGENCY"
            if st.session_state.emergency_active
            else "🟢 SAFE"
        )

        st.metric(
            "Safety Status",
            status
        )

    with c2:

        st.metric(
            "Trusted Contacts",
            len(contacts)
        )

    with c3:

        st.metric(
            "Incidents",
            len(incidents)
        )

    with c4:

        st.metric(
            "Safety Tools",
            "10+"
        )

    st.divider()

    st.subheader("🚨 Quick SOS")

    if st.session_state.emergency_active:

        st.error(
            "🔴 EMERGENCY MODE ACTIVE"
        )

        if st.button(
            "🟢 END EMERGENCY",
            use_container_width=True
        ):

            st.session_state.emergency_active = False

            st.success(
                "Emergency mode ended."
            )

            st.rerun()

    else:

        if st.button(
            "🆘 ACTIVATE SOS",
            use_container_width=True
        ):

            contacts = get_contacts()

            if not contacts:

                st.warning(
                    "Add at least one trusted contact first."
                )

            else:

                box = st.empty()

                for seconds in range(5, 0, -1):

                    box.error(
                        f"🚨 SOS ACTIVATING IN "
                        f"**{seconds} SECONDS**"
                    )

                    time.sleep(1)

                st.session_state.emergency_active = True

                add_incident(
                    "Manual SOS",
                    "Emergency button activated",
                    st.session_state.latitude,
                    st.session_state.longitude
                )

                st.rerun()

    st.divider()

    st.subheader("🛡️ Safety Tools")

    tools = [
        ("🆘", "SOS Emergency"),
        ("📍", "Live Location"),
        ("🎙️", "AI Detection"),
        ("⏱️", "Safety Timer"),
        ("🛡️", "Safe Check-In"),
        ("📞", "Fake Call"),
        ("🔊", "Alarm"),
        ("📝", "Incident Report")
    ]

    cols = st.columns(4)

    for i, (icon, name) in enumerate(tools):

        with cols[i % 4]:

            st.markdown(
                f"""
                <div class="feature-card">
                <h2>{icon}</h2>
                <b>{name}</b>
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# EMERGENCY
# =========================================================

elif page == "🆘 Emergency":

    st.header("🚨 Emergency Center")

    st.markdown(
        '<div class="sos-card">',
        unsafe_allow_html=True
    )

    if not st.session_state.emergency_active:

        st.subheader(
            "🆘 Emergency SOS"
        )

        st.write(
            "A 5-second countdown gives you time "
            "to cancel an accidental activation."
        )

        if st.button(
            "🆘 ACTIVATE EMERGENCY",
            use_container_width=True
        ):

            contacts = get_contacts()

            if not contacts:

                st.error(
                    "Please add an emergency contact."
                )

            else:

                countdown = st.empty()

                for sec in range(5, 0, -1):

                    countdown.error(
                        f"🚨 Activating in **{sec}**"
                    )

                    time.sleep(1)

                st.session_state.emergency_active = True

                add_incident(
                    "Manual SOS",
                    "Emergency activated",
                    st.session_state.latitude,
                    st.session_state.longitude
                )

                st.rerun()

    else:

        st.error(
            "🔴 EMERGENCY MODE ACTIVE"
        )

        st.write(
            "Emergency incident has been recorded."
        )

        if st.session_state.latitude:

            st.info(
                f"📍 Location: "
                f"{st.session_state.latitude:.6f}, "
                f"{st.session_state.longitude:.6f}"
            )

        contacts = get_contacts()

        st.subheader(
            "👥 Trusted Contacts"
        )

        for contact in contacts:

            st.write(
                f"👤 **{contact[1]}** | "
                f"📞 {contact[2]}"
            )

        st.divider()

        profile = get_profile()

        pin = st.text_input(
            "Enter your emergency PIN to cancel",
            type="password"
        )

        if st.button(
            "🟢 END EMERGENCY"
        ):

            if profile and pin == profile[3]:

                st.session_state.emergency_active = False

                st.success(
                    "Emergency mode ended safely."
                )

                st.rerun()

            else:

                st.error(
                    "Incorrect PIN."
                )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# CONTACTS
# =========================================================

elif page == "👥 Contacts":

    st.header("👥 Emergency Contacts")

    with st.form("contact_form"):

        name = st.text_input(
            "Contact Name"
        )

        phone = st.text_input(
            "Phone Number"
        )

        relationship = st.text_input(
            "Relationship"
        )

        submit = st.form_submit_button(
            "➕ Add Contact"
        )

        if submit:

            if name and phone:

                add_contact(
                    name,
                    phone,
                    relationship
                )

                st.success(
                    "Contact added."
                )

                st.rerun()

            else:

                st.error(
                    "Name and phone are required."
                )

    st.divider()

    contacts = get_contacts()

    for contact in contacts:

        c1, c2, c3, c4 = st.columns(
            [2, 2, 2, 1]
        )

        with c1:
            st.write(
                f"👤 **{contact[1]}**"
            )

        with c2:
            st.write(
                f"📞 {contact[2]}"
            )

        with c3:
            st.write(
                f"🤝 {contact[3]}"
            )

        with c4:

            if st.button(
                "🗑️",
                key=f"del{contact[0]}"
            ):

                delete_contact(
                    contact[0]
                )

                st.rerun()


# =========================================================
# LIVE LOCATION
# =========================================================

elif page == "📍 Live Location":

    st.header("📍 Live Location")

    location = streamlit_geolocation()

    if location:

        lat = location.get("latitude")
        lon = location.get("longitude")

        if lat is not None and lon is not None:

            st.session_state.latitude = lat
            st.session_state.longitude = lon

            st.success(
                "📍 Location detected."
            )

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "Latitude",
                    f"{lat:.6f}"
                )

            with c2:
                st.metric(
                    "Longitude",
                    f"{lon:.6f}"
                )

            st.map(
                {
                    "lat": [lat],
                    "lon": [lon]
                }
            )

            maps_url = (
                f"https://www.google.com/maps/search/"
                f"?api=1&query={lat},{lon}"
            )

            st.markdown(
                f"[🗺️ Open Location in Google Maps]({maps_url})"
            )

    else:

        st.info(
            "Please allow browser location permission."
        )


# =========================================================
# AI SAFETY
# =========================================================

elif page == "🎙️ AI Safety":

    st.header(
        "🤖 AI Emergency Detection"
    )

    st.write(
        "Speak an emergency phrase."
    )

    text = speech_to_text(
        language="en",
        start_prompt="🎙️ Start Speaking",
        stop_prompt="⏹️ Stop Recording",
        just_once=True,
        use_container_width=True,
        key="voice"
    )

    if text:

        st.subheader(
            "🗣️ Detected Speech"
        )

        st.write(text)

        emergency_words = [
            "help",
            "danger",
            "emergency",
            "save me",
            "attack",
            "threat",
            "unsafe",
            "please help",
            "call police"
        ]

        detected = [
            word
            for word in emergency_words
            if word in text.lower()
        ]

        if detected:

            st.error(
                "🚨 POSSIBLE EMERGENCY DETECTED"
            )

            st.write(
                "Detected: "
                + ", ".join(detected)
            )

            st.progress(90)

            if st.button(
                "🆘 ACTIVATE SOS FROM AI"
            ):

                st.session_state.emergency_active = True

                add_incident(
                    "AI Voice Detection",
                    text,
                    st.session_state.latitude,
                    st.session_state.longitude
                )

                st.success(
                    "🚨 Emergency mode activated."
                )

        else:

            st.success(
                "🟢 No emergency keyword detected."
            )

    st.divider()

    st.subheader(
        "Example Emergency Phrases"
    )

    for phrase in [
        "Help me",
        "I am in danger",
        "Please help",
        "Someone is attacking me",
        "Call police"
    ]:

        st.write(
            f"🎙️ {phrase}"
        )


# =========================================================
# SAFETY TIMER
# =========================================================

elif page == "⏱️ Safety Timer":

    st.header("⏱️ Safety Timer")

    st.write(
        "Set a timer for a journey or situation. "
        "You can confirm your safety before it expires."
    )

    minutes = st.number_input(
        "Timer duration (minutes)",
        min_value=1,
        max_value=120,
        value=10
    )

    if st.button(
        "▶️ Start Safety Timer"
    ):

        st.session_state.safety_timer_end = (
            datetime.now()
            + timedelta(minutes=minutes)
        )

        st.success(
            f"Safety timer started for {minutes} minutes."
        )

    if st.session_state.safety_timer_end:

        remaining = (
            st.session_state.safety_timer_end
            - datetime.now()
        ).total_seconds()

        if remaining > 0:

            mins = int(remaining // 60)
            secs = int(remaining % 60)

            st.warning(
                f"⏱️ Time remaining: "
                f"**{mins:02d}:{secs:02d}**"
            )

            if st.button(
                "🟢 I AM SAFE"
            ):

                st.session_state.safety_timer_end = None

                st.success(
                    "✅ Safety confirmed."
                )

                st.rerun()

        else:

            st.error(
                "🚨 SAFETY TIMER EXPIRED"
            )

            st.warning(
                "Please confirm your safety."
            )

            if st.button(
                "🆘 ACTIVATE EMERGENCY"
            ):

                st.session_state.emergency_active = True

                add_incident(
                    "Safety Timer",
                    "Safety timer expired",
                    st.session_state.latitude,
                    st.session_state.longitude
                )

                st.rerun()


# =========================================================
# SAFE CHECK-IN
# =========================================================

elif page == "🛡️ Safe Check-In":

    st.header("🛡️ Safe Check-In")

    destination = st.text_input(
        "Destination",
        placeholder="College / Home / Bus Stand"
    )

    duration = st.number_input(
        "Expected travel time (minutes)",
        min_value=1,
        max_value=300,
        value=30
    )

    if st.button(
        "🟢 Start Safe Journey"
    ):

        if destination:

            st.session_state.checkin_active = True

            st.session_state.checkin_destination = destination

            st.session_state.checkin_deadline = (
                datetime.now()
                + timedelta(minutes=duration)
            )

            st.success(
                f"Journey started to {destination}."
            )

        else:

            st.warning(
                "Enter a destination."
            )

    if st.session_state.checkin_active:

        st.divider()

        st.info(
            f"📍 Destination: "
            f"{st.session_state.checkin_destination}"
        )

        deadline = (
            st.session_state.checkin_deadline
        )

        remaining = (
            deadline - datetime.now()
        ).total_seconds()

        if remaining > 0:

            mins = int(remaining // 60)
            secs = int(remaining % 60)

            st.warning(
                f"⏱️ Remaining: "
                f"**{mins:02d}:{secs:02d}**"
            )

            if st.button(
                "✅ I ARRIVED SAFELY"
            ):

                st.session_state.checkin_active = False

                st.success(
                    "🎉 Safe arrival confirmed."
                )

                st.rerun()

        else:

            st.error(
                "⚠️ Expected arrival time has passed."
            )

            if st.button(
                "🆘 I NEED HELP"
            ):

                st.session_state.emergency_active = True

                add_incident(
                    "Safe Check-In",
                    "Expected arrival time passed",
                    st.session_state.latitude,
                    st.session_state.longitude
                )

                st.rerun()


# =========================================================
# FAKE CALL
# =========================================================

elif page == "📞 Fake Call":

    st.header("📞 Fake Call / Escape Mode")

    st.write(
        "A simulated incoming-call screen can be used "
        "as an exit strategy from an uncomfortable situation."
    )

    caller = st.text_input(
        "Caller name",
        value="Mom"
    )

    if not st.session_state.fake_call:

        if st.button(
            "📞 START FAKE CALL"
        ):

            st.session_state.fake_call = True

            st.rerun()

    else:

        st.markdown(
            f"""
            <div class="fake-call">
            <h1>📞</h1>
            <h2>Incoming Call</h2>
            <h1>{caller}</h1>
            <p>Mobile Phone</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "📞 Answer",
                use_container_width=True
            ):

                st.success(
                    f"Call answered from {caller}."
                )

        with c2:

            if st.button(
                "❌ End",
                use_container_width=True
            ):

                st.session_state.fake_call = False

                st.rerun()


# =========================================================
# INCIDENT REPORT
# =========================================================

elif page == "📝 Incident Report":

    st.header("📝 Incident Report")

    incident_type = st.selectbox(
        "Incident Type",
        [
            "Harassment",
            "Threat",
            "Unsafe Location",
            "Suspicious Activity",
            "Accident",
            "Other"
        ]
    )

    description = st.text_area(
        "Describe the incident"
    )

    if st.button(
        "💾 Save Incident Report"
    ):

        add_incident(
            incident_type,
            description,
            st.session_state.latitude,
            st.session_state.longitude,
            "REPORTED"
        )

        st.success(
            "Incident report saved."
        )


# =========================================================
# INCIDENT HISTORY
# =========================================================

elif page == "📋 Incident History":

    st.header(
        "📋 Incident History"
    )

    incidents = get_incidents()

    if incidents:

        for incident in incidents:

            with st.expander(
                f"🚨 {incident[1]} — {incident[5]}"
            ):

                st.write(
                    f"**Description:** "
                    f"{incident[2]}"
                )

                st.write(
                    f"**Latitude:** "
                    f"{incident[3]}"
                )

                st.write(
                    f"**Longitude:** "
                    f"{incident[4]}"
                )

                st.write(
                    f"**Status:** "
                    f"{incident[6]}"
                )

    else:

        st.info(
            "No incidents recorded."
        )


# =========================================================
# ANALYTICS
# =========================================================

elif page == "📊 Analytics":

    st.header(
        "📊 Safety Analytics"
    )

    incidents = get_incidents()

    if incidents:

        df = pd.DataFrame(
            incidents,
            columns=[
                "ID",
                "Type",
                "Description",
                "Latitude",
                "Longitude",
                "Time",
                "Status"
            ]
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Total Incidents",
                len(df)
            )

        with c2:

            st.metric(
                "SOS Events",
                int(
                    df["Type"]
                    .astype(str)
                    .str.contains(
                        "SOS",
                        case=False
                    )
                    .sum()
                )
            )

        with c3:

            st.metric(
                "AI Events",
                int(
                    df["Type"]
                    .astype(str)
                    .str.contains(
                        "AI",
                        case=False
                    )
                    .sum()
                )
            )

        st.subheader(
            "Incident Type"
        )

        chart = (
            df["Type"]
            .value_counts()
        )

        st.bar_chart(chart)

        st.subheader(
            "Incident Records"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info(
            "No data available yet."
        )


# =========================================================
# PROFILE
# =========================================================

elif page == "👤 Profile":

    st.header(
        "👤 User Profile"
    )

    profile = get_profile()

    name = st.text_input(
        "Name",
        value=profile[0] if profile else ""
    )

    phone = st.text_input(
        "Phone",
        value=profile[1] if profile else ""
    )

    email = st.text_input(
        "Email",
        value=profile[2] if profile else ""
    )

    pin = st.text_input(
        "Emergency PIN",
        type="password"
    )

    st.info(
        "The PIN is used to cancel an active SOS."
    )

    if st.button(
        "💾 Save Profile"
    ):

        if len(pin) >= 4:

            save_profile(
                name,
                phone,
                email,
                pin
            )

            st.success(
                "Profile saved."
            )

        else:

            st.error(
                "PIN must contain at least 4 characters."
            )


# =========================================================
# SETTINGS
# =========================================================

elif page == "⚙️ Settings":

    st.header(
        "⚙️ Settings"
    )

    st.session_state.safe_mode = st.toggle(
        "🛡️ Safe Mode",
        value=st.session_state.safe_mode
    )

    st.session_state.ai_enabled = st.toggle(
        "🤖 AI Detection",
        value=True
    )

    alarm = st.toggle(
        "🔊 Emergency Alarm",
        value=False
    )

    st.divider()

    st.subheader(
        "🔊 Alarm Test"
    )

    if st.button(
        "🔊 ACTIVATE ALARM"
    ):

        st.error(
            "🚨 ALARM ACTIVE — "
            "connect a device/browser audio service "
            "for real sound output."
        )

    st.divider()

    st.subheader(
        "ℹ️ About"
    )

    st.write(
        """
        SafeHer AI is an academic AIML prototype
        combining emergency assistance, location,
        trusted contacts, voice keyword detection,
        safety timers, check-ins and incident management.
        """
    )

    st.warning(
        "This application is a safety-assistance prototype "
        "and does not replace official emergency services."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🛡️ SafeHer AI | Women Safety & Emergency Assistance | AIML Project"
)