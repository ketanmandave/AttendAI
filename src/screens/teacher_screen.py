import streamlit as st
from src.database.db import check_teacher_exists, create_teacher, teacher_login
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
    style_teacher_auth,
)


def teacher_screen():

    style_background_dashboard()
    style_base_layout()
    style_teacher_auth()
    if 'teacher_data' in st.session_state:
        teacher_dashboard()
    elif(
        "teacher_login_type" not in st.session_state
        or st.session_state.teacher_login_type == "login"
    ):
        teacher_screen_login()

    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()

    else:
        st.session_state["teacher_login_type"] = None
        st.rerun()



def teacher_dashboard():
    teacher_data = st.session_state.teacher_data

    st.header(f"Welcome, {teacher_data['name']}!")


# =========================================================
# LOGIN
# =========================================================


def teacher_login_db(username, password):
    if not username or not password:
        return False, "Please enter both username and password."

    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.is_logged_in = True
        st.session_state.teacher_data= teacher
        st.session_state.user_role = 'teacher'
        return True, f"Welcome back, {teacher['name']}!"
    else:
        return False, "Invalid username or password."


def teacher_screen_login():

    # Header row
    col1, col2 = st.columns([5, 1])

    with col1:
        header_dashboard()

    with col2:
        st.write("")

        if st.button("← Home", key="loginBackButton", width="stretch"):
            st.session_state["login_type"] = None
            st.rerun()

    # Page intro
    st.html("""
        <div class="teacher-auth-heading">

            <div class="teacher-auth-icon">
                👨‍🏫
            </div>

            <div>
                <p class="teacher-auth-label">
                    TEACHER ACCESS
                </p>

                <h2>
                    Welcome back
                </h2>

                <p>
                    Sign in to manage attendance and student records.
                </p>
            </div>

        </div>
        """)

    # Form container
    with st.container(border=True):

        st.markdown("#### Login Details")

        username = st.text_input(
            "Username", placeholder="Enter your username", key="teacherUsername"
        )

        password = st.text_input(
            "Password",
            placeholder="Enter your password",
            type="password",
            key="teacherPassword",
        )

        st.write("")

        col1, col2 = st.columns(2)

        with col1:

            if st.button("Login", key="loginButton", width="stretch"):
                success, message = teacher_login_db(username, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

        with col2:

            if st.button("Create Account", key="registerButton", width="stretch"):
                st.session_state.teacher_login_type = "register"
                st.rerun()

    # Small info section
    st.html("""
        <div class="teacher-auth-info">

            <div>
                <span>🔐</span>

                <div>
                    <strong>Secure Access</strong>
                    <p>
                        Teacher credentials protect attendance controls.
                    </p>
                </div>
            </div>

            <div>
                <span>📊</span>

                <div>
                    <strong>Attendance Management</strong>
                    <p>
                        View and manage student attendance records.
                    </p>
                </div>
            </div>

        </div>
        """)

    footer_dashboard()


# =========================================================
# REGISTER
# =========================================================


def register_teacher(name, username, password, confirm):
    if not name or not username or not password or not confirm:
        return False, "All fields are required."

    if password != confirm:
        return False, "Passwords do not match."

    if check_teacher_exists(username):
        return False, "Username already exists."

    teacher = create_teacher(username, password, name)
    if teacher:
        st.session_state.teacher_login_type = "login"
        st.rerun()
        return True, "Teacher account created successfully."
    else:
        return False, "Failed to create teacher account."


def teacher_screen_register():

    # Header row
    col1, col2 = st.columns([5, 1])

    with col1:
        header_dashboard()

    with col2:
        st.write("")

        if st.button("← Home", key="registerHomeButton", width="stretch"):
            st.session_state["login_type"] = None
            st.rerun()

    # Page heading
    st.html("""
        <div class="teacher-auth-heading">

            <div class="teacher-auth-icon">
                ✨
            </div>

            <div>
                <p class="teacher-auth-label">
                    NEW TEACHER
                </p>

                <h2>
                    Create your account
                </h2>

                <p>
                    Register as a teacher to access AttendIQ.
                </p>
            </div>

        </div>
        """)

    # Form container
    with st.container(border=True):

        st.markdown("#### Teacher Information")

        name = st.text_input(
            "Full Name", placeholder="Enter your full name", key="teacherName"
        )

        username = st.text_input(
            "Username", placeholder="Choose a username", key="teacherRegisterUsername"
        )

        col1, col2 = st.columns(2)

        with col1:

            password = st.text_input(
                "Password",
                placeholder="Create a password",
                type="password",
                key="teacherRegisterPassword",
            )

        with col2:

            confirm = st.text_input(
                "Confirm Password",
                placeholder="Re-enter password",
                type="password",
                key="teacherConfirmPassword",
            )

        st.write("")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Create Teacher Account", key="teacherCreateButton", width="stretch"
            ):
                success, message = register_teacher(name, username, password, confirm)
                if success:
                    st.success(message)
                else:
                    st.error(message)

        with col2:

            if st.button("Back to Login", key="backLoginButton", width="stretch"):
                st.session_state.teacher_login_type = "login"
                st.rerun()

    footer_dashboard()
