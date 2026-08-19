import streamlit as st


def header_home():

    st.html(
        """
        <div style="text-align:center; margin-bottom:30px;">

            <h1 style="
                color:white;
                font-size:48px;
                margin-bottom:5px;
            ">
                AttendIQ
            </h1>

            <p style="
                color:#cbd5e1;
                font-size:16px;
            ">
                Smart Face & Voice Based Attendance System
            </p>

        </div>
        """
    )