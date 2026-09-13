import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timezone, timedelta

# Database connect functions
def get_db():
    connection = sqlite3.connect(db_name)
    connection.execute("PRAGMA journal_mode=WAL;")

    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            timezone INTEGER NOT NULL)
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            in_timestamp INTEGER NOT NULL,
            out_timestamp INTEGER NOT NULL,
            creator_id INTEGER NOT NULL)
        """)

    return connection

# Login function
def login():
    if not your_username:
        return

    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT EXISTS(SELECT * FROM profiles WHERE username = ?)
            """, (your_username,))
        username_exists = cursor.fetchone()[0]

        if username_exists:
            cursor.execute("""
                SELECT * FROM profiles WHERE username = ?
                """, (your_username,))
            query = cursor.fetchone()
            your_name = query[2]
            your_timezone = query[3]
            st.session_state.session_info = [your_username, your_name, your_timezone, int(datetime.now().timestamp())]
        else:
            st.session_state.session_info = [your_username, "NULL", 0, int(datetime.now().timestamp())]

# Sign up function
def signup():
    with get_db() as connection:
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        query = [(your_username, your_name, your_timezone)]
        cursor.executemany("""
            INSERT INTO profiles (username, name, timezone)
            VALUES (?, ?, ?)
            """, query)
        connection.commit()
        st.session_state.session_info = [your_username, your_name, your_timezone, int(datetime.now().timestamp())]

# Check login info:
def check_session():
    if (int(datetime.now().timestamp()) - st.session_state.session_info[3]) > 3600:
        wipe_session()
        return False
    else:
        return True

# Clear login info:
def wipe_session():
    st.session_state.session_info = []

# Get session timezone info
def session_tz():
    return timezone(timedelta(hours = st.session_state.session_info[2]))

# Working-hour conflict error checking
def schedule_err(hour):
    if 8 <= hour < 17:
        return False
    else:
        return True

# Get guest info
def findguest(guest_name):
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT EXISTS(SELECT * FROM profiles WHERE name = ?)
            """, (guest_name,))
        name_exists = cursor.fetchone()[0]

        if name_exists:
            cursor.execute("""
                SELECT * FROM profiles WHERE name = ?
                """, (guest_name,))
            query = cursor.fetchone()
            return [query[1], guest_name, query[3], int(datetime.now().timestamp())]
        else:
            return False

# Check schedule function
def checkschedules():
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT EXISTS(SELECT * FROM schedules WHERE username = ?)
            """, (st.session_state.session_info[0],))
        schedules_exists = cursor.fetchone()[0]

        if schedules_exists:
            cursor.execute("""
            SELECT * FROM schedules WHERE username = ?
            """, (st.session_state.session_info[0],))
            allschedules = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            df = pd.DataFrame(allschedules, columns = columns)
            df["in_timestamp"] = pd.to_datetime(df["in_timestamp"], unit="s")
            df["in_timestamp"] = df["in_timestamp"] + pd.Timedelta(hours = st.session_state.session_info[2])
            df["out_timestamp"] = pd.to_datetime(df["out_timestamp"], unit="s")
            df["out_timestamp"] = df["out_timestamp"] + pd.Timedelta(hours = st.session_state.session_info[2])
            df["date"] = df["in_timestamp"].dt.date
            df["in_time"] = df["in_timestamp"].dt.time
            df["out_time"] = df["out_timestamp"].dt.time
            df["creator_id"] = df["creator_id"].astype(bool)

            return df[["date", "in_time", "out_time", "creator_id"]].copy()
        else:
            return

# Query new schedule function
def schedule(user_info, creator):
    with get_db() as connection:
        cursor = connection.cursor()

        query = [(user_info[0], in_timestamp, out_timestamp, creator)]
        cursor.executemany("""
            INSERT INTO schedules (username, in_timestamp, out_timestamp, creator_id)
            VALUES (?, ?, ?, ?)
            """, query)
        connection.commit()

# Initalize variables
db_name = "database.db"

if "current_pg" not in st.session_state or "session_info" not in st.session_state or "guestlist" not in st.session_state:
    st.session_state.current_pg = 1
    st.session_state.session_info = []
    st.session_state.guestlist = []

# Login page
if st.session_state.current_pg == 1:
    st.title("User Login")
    with st.form(key = "login_form"):
        your_username = st.text_input("Insert username: ")
        login_button = st.form_submit_button(label = "Login")

    if login_button:
        if your_username.strip() == "":
            st.warning("Please enter a username!")
        else:
            login()

    if st.session_state.session_info != []:
        if st.session_state.session_info[1] == "NULL":
            st.warning("Redirecting you to a sign up page...")
            st.session_state.current_pg = 9
            st.rerun()
        else:
            st.success(f"Welcome back {st.session_state.session_info[1]}!")
            st.session_state.current_pg = 2
            st.rerun()

# Sign up page
elif st.session_state.current_pg == 9:
    st.title("Sign Up")
    with st.form(key = "signup_form"):
        your_name = st.text_input("Insert name: ")
        your_timezone = int(st.number_input(label = "Your timezone is: GMT+", min_value = -12, max_value = 12, step = 1, value = 0))
        signup_button = st.form_submit_button(label = "Sign Up")

    if signup_button:
        if your_name.strip() == "" or your_timezone is None:
            st.warning("Please fill in the required form!")
        else:
            your_username = st.session_state.session_info[0]
            signup()

    if st.session_state.session_info[1] != "NULL":
        st.success(f"Sign up complete! Hello {your_name}!")
        st.session_state.current_pg = 2
        st.rerun()

# Main page
elif st.session_state.current_pg == 2:
    st.title(f"Hello {st.session_state.session_info[1]}!")
    df = checkschedules()
    if df is not None:
        df.columns = ["Appointment Date", "Starts in", "Ends at", "Is Creator"]
        st.write(f"{st.session_state.session_info[1]}, you have an appointment in:")
        st.dataframe(df)
    else:
        st.write("You don't have any appointments scheduled.")

    if check_session() == False:
        st.warning("Your session has expired. Please login again.")
        st.session_state.current_pg = 1
        st.rerun()

    with st.form(key = "goto_schedule"):
        goto_button = st.form_submit_button(label = "Add a new appointment")
        logout_button = st.form_submit_button(label = "Logout")
    
    if goto_button:
        st.session_state.current_pg = 3
        st.rerun()
    elif logout_button:
        st.info("Logging you out...")
        wipe_session()
        st.session_state.current_pg = 1
        st.rerun()

# Scheduling page
elif st.session_state.current_pg == 3:
    if check_session() == False:
        st.warning("Your session has expired. Please login again.")
        st.session_state.current_pg = 1
        st.rerun()

    st.title("New Appointment")
    with st.form(key = "appt_form"):
        in_year = int(st.number_input(label = "Year: ", min_value = 1970, step = 1, value = datetime.now().year))
        in_month = int(st.number_input(label = "Month: ", min_value = 1, max_value = 12, step = 1, value = datetime.now().month))
        in_day = int(st.number_input(label = "Day: ", min_value = 1, max_value = 31, step = 1, value = datetime.now().day))
        in_hour = int(st.number_input(label = "Starting Hour (24-hour format): ", min_value = 0, max_value = 23, step = 1, value = 8))
        out_hour = int(st.number_input(label = "End Hour (24-hour format): ", min_value = 0, max_value = 23, step = 1, value = 16))
        new_guest = st.text_input("Insert name: ")
        guest_button = st.form_submit_button(label = "Add Guest")
        appoint_button = st.form_submit_button(label = "Confirm Appointment")
        goback_button = st.form_submit_button(label = "Back")

    if guest_button:
        guest_info = findguest(new_guest)
        if guest_info == False:
            st.warning(f"Oops! Apparently {new_guest} is not a valid user. Please try again.")
        else:
            if schedule_err(in_hour + guest_info[2] - st.session_state.session_info[2]) == False and schedule_err(out_hour + guest_info[2] - st.session_state.session_info[2]) == False:
                st.info(f"Adding {new_guest} to your appointment...")
                update_list = list(st.session_state.guestlist)
                update_list.append(guest_info)
                st.session_state.guestlist = update_list
            else:
                st.warning(f"Scheduled time out of established working hours for {new_guest}!")

    elif appoint_button:
        in_timestamp = int(datetime(in_year, in_month, in_day, in_hour, 0, 0, tzinfo = session_tz()).timestamp())
        out_timestamp = int(datetime(in_year, in_month, in_day, out_hour, 0, 0, tzinfo = session_tz()).timestamp())
        if in_timestamp > int(datetime.now().timestamp()) and out_timestamp > int(datetime.now().timestamp()):
            if schedule_err(in_hour) == False and schedule_err(out_hour) == False:
                for addguest in st.session_state.guestlist:
                    schedule(addguest, creator = 0)

                schedule(st.session_state.session_info, creator = 1)
                st.session_state.guestlist = []
                st.session_state.current_pg = 2
                st.rerun()
            else:
                st.warning("Scheduled time out of established working hours!")
        else:
            st.warning("Scheduling error! Please try again.")

    elif goback_button:
        st.session_state.current_pg = 2
        st.rerun()




