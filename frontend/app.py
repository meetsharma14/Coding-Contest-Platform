import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "https://coding-contest-platform-gv03.onrender.com/"


# ==========================
# SESSION STATE
# ==========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "token" not in st.session_state:
    st.session_state.token = None


# ==========================
# HOME
# ==========================

def home():

    st.title("Coding Contest Platform ")

    st.write(
        """
        Welcome to Coding Contest Platform
        
        Features:
        - Coding Problems
        - Contests
        - Submissions
        - Leaderboards
        """
    )


# ==========================
# REGISTER
# ==========================

def register():

    st.header("Register")

    username = st.text_input(
        "Username"
    )

    email = st.text_input(
        "Email"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Register"):

        payload = {
            "username": username,
            "email": email,
            "password": password
        }

        r = requests.post(
            f"{API_BASE_URL}/users/register",
            json=payload
        )

        if r.status_code in [200,201]:

            st.success(
                "Registration successful"
            )

        else:
            st.error(
                r.text
            )


# ==========================
# LOGIN
# ==========================

def login():

    st.header("Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        payload = {
            "username": username,
            "password": password
        }

        r = requests.post(
            f"{API_BASE_URL}/users/login",
            json=payload
        )

        if r.status_code == 200:

            data = r.json()

            st.session_state.token = (
                data["access_token"]
            )

            st.session_state.logged_in = True

            st.success(
                "Login successful"
            )

            st.rerun()

        else:

            st.error(
                "Invalid credentials"
            )


# ==========================
# LOGOUT
# ==========================

def logout():

    st.session_state.logged_in = False
    st.session_state.token = None

    st.success(
        "Logged out"
    )

    st.rerun()


# ==========================
# PROBLEMS
# ==========================

def problems_page():

    st.header("Problems")

    try:

        r = requests.get(
            f"{API_BASE_URL}/problems/"
        )

        if r.status_code == 200:

            data = r.json()

            if len(data) > 0:

                df = pd.DataFrame(
                    data
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

                problem_id = st.number_input(
                    "Problem ID",
                    min_value=1,
                    step=1
                )

                if st.button(
                    "Load Problem"
                ):

                    pr = requests.get(
                        f"{API_BASE_URL}/problems/{problem_id}"
                    )

                    if pr.status_code == 200:

                        p = pr.json()

                        st.subheader(
                            p["title"]
                        )

                        st.write(
                            f"Difficulty: {p['difficulty']}"
                        )

                        st.write(
                            p["description"]
                        )

                        st.code(
                            p["sample_input"]
                        )

                        st.code(
                            p["sample_output"]
                        )

                    else:

                        st.error(
                            "Problem not found"
                        )

            else:

                st.warning(
                    "No problems found"
                )

        else:
            st.error(r.text)

    except Exception as e:

        st.error(
            str(e)
        )


# ==========================
# ADMIN PANEL
# ==========================

def _admin_headers():
    """Return Authorization header using the current session token."""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _admin_dashboard():
    """Overview tab with platform statistics."""

    st.subheader("Platform Overview")

    headers = _admin_headers()

    col1, col2, col3 = st.columns(3)

    # Fetch problems count
    try:
        r = requests.get(f"{API_BASE_URL}/problems/")
        problems = r.json() if r.status_code == 200 else []
    except Exception:
        problems = []

    # Fetch contests count
    try:
        r = requests.get(f"{API_BASE_URL}/contests/")
        contests = r.json() if r.status_code == 200 else []
    except Exception:
        contests = []

    # Fetch leaderboard for user count
    try:
        r = requests.get(f"{API_BASE_URL}/leaderboard/")
        users = r.json() if r.status_code == 200 else []
    except Exception:
        users = []

    with col1:
        st.metric("Total Problems", len(problems))
    with col2:
        st.metric("Total Contests", len(contests))
    with col3:
        st.metric("Total Users", len(users))

    # Active contests
    st.markdown("---")
    st.subheader("Active Contests")
    try:
        r = requests.get(f"{API_BASE_URL}/contests/active/list")
        active = r.json() if r.status_code == 200 else []
    except Exception:
        active = []

    if active:
        df = pd.DataFrame(active)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No active contests right now.")

    # Recent problems
    st.markdown("---")
    st.subheader("Recent Problems")
    if problems:
        df = pd.DataFrame(problems)
        display_cols = [c for c in ["id", "title", "difficulty"] if c in df.columns]
        st.dataframe(df[display_cols].tail(5), use_container_width=True)
    else:
        st.info("No problems created yet.")


def _admin_problems():
    """Problem management tab: list, create, delete."""

    headers = _admin_headers()

    # ------- Existing problems -------
    st.subheader("Existing Problems")
    try:
        r = requests.get(f"{API_BASE_URL}/problems/")
        problems = r.json() if r.status_code == 200 else []
    except Exception:
        problems = []

    if problems:
        df = pd.DataFrame(problems)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No problems found.")

    # ------- Add problem -------
    st.markdown("---")
    st.subheader("Add New Problem")

    with st.form("add_problem_form", clear_on_submit=True):
        title = st.text_input("Problem Title")
        difficulty = st.selectbox(
            "Difficulty", ["Easy", "Medium", "Hard"]
        )
        description = st.text_area("Description")
        sample_input = st.text_area("Sample Input")
        sample_output = st.text_area("Sample Output")
        submitted = st.form_submit_button("Add Problem")

    if submitted:
        if not title or not description:
            st.error("Title and Description are required.")
        else:
            payload = {
                "title": title,
                "difficulty": difficulty,
                "description": description,
                "sample_input": sample_input,
                "sample_output": sample_output,
            }
            r = requests.post(
                f"{API_BASE_URL}/problems/",
                json=payload,
                headers=headers,
            )
            if r.status_code in [200, 201]:
                st.success("Problem added successfully!")
                st.json(r.json())
            else:
                st.error(f"Failed to add problem: {r.text}")

    # ------- Delete problem -------
    st.markdown("---")
    st.subheader("Delete Problem")

    with st.form("delete_problem_form"):
        del_id = st.number_input(
            "Problem ID to delete", min_value=1, step=1
        )
        del_submitted = st.form_submit_button("Delete Problem")

    if del_submitted:
        r = requests.delete(
            f"{API_BASE_URL}/problems/{del_id}",
            headers=headers,
        )
        if r.status_code == 200:
            st.success(f"Problem {del_id} deleted.")
        elif r.status_code == 404:
            st.error("Problem not found.")
        elif r.status_code in [401, 403]:
            st.error("Admin access required to delete problems.")
        else:
            st.error(f"Error: {r.text}")


def _admin_contests():
    """Contest management tab: list, create, add problems, start/end."""

    headers = _admin_headers()

    # ------- Existing contests -------
    st.subheader("Existing Contests")
    try:
        r = requests.get(f"{API_BASE_URL}/contests/")
        contests = r.json() if r.status_code == 200 else []
    except Exception:
        contests = []

    if contests:
        df = pd.DataFrame(contests)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No contests found.")

    # ------- Create contest -------
    st.markdown("---")
    st.subheader("Create Contest")

    with st.form("create_contest_form", clear_on_submit=True):
        title = st.text_input("Contest Title")
        description = st.text_area("Contest Description")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
            start_time = st.time_input("Start Time")
        with col2:
            end_date = st.date_input("End Date")
            end_time = st.time_input("End Time")
        submitted = st.form_submit_button("Create Contest")

    if submitted:
        if not title:
            st.error("Contest title is required.")
        else:
            from datetime import datetime

            start_dt = datetime.combine(start_date, start_time).isoformat()
            end_dt = datetime.combine(end_date, end_time).isoformat()
            payload = {
                "title": title,
                "description": description,
                "start_time": start_dt,
                "end_time": end_dt,
            }
            r = requests.post(
                f"{API_BASE_URL}/contests/",
                json=payload,
                headers=headers,
            )
            if r.status_code in [200, 201]:
                st.success("Contest created successfully!")
                st.json(r.json())
            elif r.status_code in [401, 403]:
                st.error("Admin access required to create contests.")
            else:
                st.error(f"Error: {r.text}")

    # ------- Add problem to contest -------
    st.markdown("---")
    st.subheader("Add Problem to Contest")

    with st.form("add_problem_to_contest_form"):
        contest_id = st.number_input(
            "Contest ID", min_value=1, step=1, key="ap_contest"
        )
        problem_id = st.number_input(
            "Problem ID", min_value=1, step=1, key="ap_problem"
        )
        link_submitted = st.form_submit_button("Add Problem to Contest")

    if link_submitted:
        r = requests.post(
            f"{API_BASE_URL}/contests/{contest_id}/add-problem/{problem_id}",
            headers=headers,
        )
        if r.status_code == 200:
            st.success(
                f"Problem {problem_id} added to Contest {contest_id}."
            )
        elif r.status_code == 404:
            st.error("Contest or Problem not found.")
        elif r.status_code in [401, 403]:
            st.error("Admin access required.")
        else:
            st.error(f"Error: {r.text}")

    # ------- Start / End contest -------
    st.markdown("---")
    st.subheader("Start / End Contest")

    with st.form("start_end_contest_form"):
        se_contest_id = st.number_input(
            "Contest ID", min_value=1, step=1, key="se_contest"
        )
        col1, col2 = st.columns(2)
        with col1:
            start_btn = st.form_submit_button("Start Contest")
        with col2:
            end_btn = st.form_submit_button("End Contest")

    if start_btn:
        r = requests.put(
            f"{API_BASE_URL}/contests/{se_contest_id}/start",
            headers=headers,
        )
        if r.status_code == 200:
            st.success(f"Contest {se_contest_id} started!")
        elif r.status_code == 404:
            st.error("Contest not found.")
        elif r.status_code in [401, 403]:
            st.error("Admin access required.")
        else:
            st.error(f"Error: {r.text}")

    if end_btn:
        r = requests.put(
            f"{API_BASE_URL}/contests/{se_contest_id}/end",
            headers=headers,
        )
        if r.status_code == 200:
            st.success(f"Contest {se_contest_id} ended.")
        elif r.status_code == 404:
            st.error("Contest not found.")
        elif r.status_code in [401, 403]:
            st.error("Admin access required.")
        else:
            st.error(f"Error: {r.text}")


def admin_panel():

    st.header("Admin Panel")

    if not st.session_state.get("token"):
        st.warning("Please log in to access the Admin Panel.")
        return

    tab1, tab2, tab3 = st.tabs(
        ["Dashboard", "Problems", "Contests"]
    )

    with tab1:
        _admin_dashboard()

    with tab2:
        _admin_problems()

    with tab3:
        _admin_contests()


# ==========================
# CONTESTS
# ==========================

def contests_page():

    st.header(
        "Contests"
    )

    st.info(
        "Contest module coming soon"
    )


# ==========================
# SUBMISSIONS
# ==========================

def submissions_page():

    st.header(
        "Submissions"
    )

    st.info(
        "Submission module coming soon"
    )


# ==========================
# LEADERBOARD
# ==========================

def leaderboard_page():

    st.header(
        "Leaderboard"
    )

    st.info(
        "Leaderboard module coming soon"
    )


# ==========================
# SIDEBAR MENU
# ==========================

if not st.session_state.logged_in:

    menu = [
        "Login",
        "Register"
    ]

else:

    menu = [
        "Home",
        "Problems",
        "Contests",
        "Submissions",
        "Leaderboard",
        "Admin Panel",
        "Logout"
    ]


choice = st.sidebar.selectbox(
    "Menu",
    menu
)


# ==========================
# ROUTING
# ==========================

if choice == "Login":
    login()

elif choice == "Register":
    register()

elif choice == "Home":
    home()

elif choice == "Problems":
    problems_page()

elif choice == "Contests":
    contests_page()

elif choice == "Submissions":
    submissions_page()

elif choice == "Leaderboard":
    leaderboard_page()

elif choice == "Admin Panel":
    admin_panel()

elif choice == "Logout":
    logout()
