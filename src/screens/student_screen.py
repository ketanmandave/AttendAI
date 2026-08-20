import streamlit as st
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
)

import numpy as np
from PIL import Image

def student_screen():
    style_background_dashboard()
    style_base_layout()

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

    st.header("Login using Face ID")
    photo_source = st.camera_input("Position your face in the screen")
    if photo_source:
        np.array(Image.open(photo_source))


    footer_dashboard()

    
