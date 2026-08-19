import streamlit as st


def style_background_home():

    st.markdown(
        """
        <style>

        .stApp {

            background:
                linear-gradient(
                    135deg,
                    #0f172a,
                    #1e3a8a
                );

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def style_background_dashboard():

    st.markdown(
        """
        <style>

        .stApp {
            background:#f1f5f9;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def style_base_layout():

    st.markdown(
        """
        <style>

        #MainMenu {
            visibility:hidden;
        }

        footer {
            visibility:hidden;
        }

        header {
            visibility:hidden;
        }

        .block-container {
            padding-top:30px;
            max-width:1000px;
        }

        .stButton button {

            background:#2563eb;

            color:white;

            border:none;

            border-radius:10px;

            height:45px;

            font-weight:600;

        }

        .stButton button:hover {

            background:#1d4ed8;

            color:white;

        }

        img {

            border-radius:15px;

        }

        </style>
        """,
        unsafe_allow_html=True,
    )
