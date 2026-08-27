import streamlit as st

st.set_page_config(
    page_title="AttendIQ | Smart Attendance",
    layout="wide",
    initial_sidebar_state="collapsed",
)


from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.screens.home_screen import home_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog
from src.auth.session_manager import restore_teacher_session

def main():

    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None

    # SESSION MANAGEMENT: Rebuild teacher_data from the signed-in browser's
    # revocable cookie before deciding which screen to render.
    restore_teacher_session()

    match st.session_state["login_type"]:

        case "teacher":
            teacher_screen()

        case "student":
            student_screen()

        case None:
            home_screen()

    join_code = str(st.query_params.get("join-code", "")).strip().upper()
    if join_code:
        if st.session_state["login_type"] != "student":
            st.session_state["login_type"] = "student"
            st.rerun()

        if (
            st.session_state.get("is_logged_in")
            and st.session_state.get("user_role") == "student"
            and st.session_state.get("student_data")
        ):
            auto_enroll_dialog(join_code)

if __name__ == "__main__":
    main()
