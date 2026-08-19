import streamlit as st


def footer_home():

    st.html(
        """
        <div style="
            margin-top:50px;
            text-align:center;
            color:#dbeafe;
        ">

            <hr style="
                border:none;
                height:1px;
                background:#ffffff40;
            ">

            <p style="font-size:14px;">
                AttendIQ
            </p>

            <p style="
                font-size:12px;
                color:#bfdbfe;
            ">
                Smart recognition. Reliable attendance.
            </p>

            <p style="
                font-size:11px;
                color:#93c5fd;
            ">
                © 2026 AttendIQ
            </p>

        </div>
        """
    )