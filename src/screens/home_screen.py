import streamlit as st

from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import (
    style_background_home,
    style_base_layout
)


def home_screen():

    style_background_home()
    style_base_layout()

    header_home()

    st.markdown(
        """
        <h2 style="
            text-align:center;
            color:white;
            margin-bottom:30px;
        ">
            Choose Your Portal
        </h2>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    # -------------------------
    # Teacher
    # -------------------------

    with col1:

        st.markdown(
            """
            <h3 style="
                text-align:center;
                color:white;
            ">
                Teacher Portal
            </h3>
            """,
            unsafe_allow_html=True,
        )

        st.image(
            "https://images.unsplash.com/photo-1524178232363-1fb2b075b655",
            use_container_width=True,
        )

        st.markdown(
            """
            <p style="
                text-align:center;
                color:#dbeafe;
            ">
                Manage attendance and view student records.
            </p>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open Teacher Portal",
            use_container_width=True
        ):

            st.session_state["login_type"] = "teacher"
            st.rerun()

    # -------------------------
    # Student
    # -------------------------

    with col2:

        st.markdown(
            """
            <h3 style="
                text-align:center;
                color:white;
            ">
                Student Portal
            </h3>
            """,
            unsafe_allow_html=True,
        )

        st.image(
            "https://images.unsplash.com/photo-1523240795612-9a054b0db644",
            use_container_width=True,
        )

        st.markdown(
            """
            <p style="
                text-align:center;
                color:#dbeafe;
            ">
                Verify your face and voice to mark attendance.
            </p>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open Student Portal",
            use_container_width=True
        ):

            st.session_state["login_type"] = "student"
            st.rerun()

    footer_home()