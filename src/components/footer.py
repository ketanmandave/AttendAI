import streamlit as st


def _footer():
    st.html(
        """
        <div class="ai-footer">
            <span class="ai-footer-brand">AttendIQ</span>
            <span>Face and voice assisted attendance</span>
            <span>© 2026</span>
        </div>
        <style>
        .ai-footer { display:flex; justify-content:center; align-items:center; gap:10px; flex-wrap:wrap; margin-top:34px; padding:18px 0 4px; border-top:1px solid #dfe3e1; color:#7a8381; font-size:10px; }
        .ai-footer span + span::before { content:'·'; margin-right:10px; color:#b2b9b7; }
        .ai-footer-brand { color:#34403e; font-weight:750; }
        </style>
        """
    )


def footer_home():
    _footer()


def footer_dashboard():
    _footer()
