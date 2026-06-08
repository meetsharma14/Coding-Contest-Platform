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

def admin_panel():

    st.header(
        "Admin Panel"
    )

    title = st.text_input(
        "Problem Title"
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    description = st.text_area(
        "Description"
    )

    sample_input = st.text_area(
        "Sample Input"
    )

    sample_output = st.text_area(
        "Sample Output"
    )

    if st.button(
        "Add Problem"
    ):

        payload = {
            "title": title,
            "difficulty": difficulty,
            "description": description,
            "sample_input": sample_input,
            "sample_output": sample_output
        }

        r = requests.post(
            f"{API_BASE_URL}/problems/",
            json=payload
        )

        if r.status_code in [200,201]:

            st.success(
                "Problem Added Successfully"
            )

            st.json(
                r.json()
            )

        else:

            st.error(
                r.text
            )


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
