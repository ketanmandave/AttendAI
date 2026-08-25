from html import escape

import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):

    name = escape(str(name))
    code = escape(str(code))
    section = escape(str(section))

    html = f"""
    <div style="
        background:white;
        border-left:4px solid #0f766e;
        padding:18px;
        border-radius:12px;
        border:1px solid #e2e8f0;
        margin-bottom:12px;
    ">

        <h3 style="
            margin:0;
            color:#1e293b;
            font-size:1.15rem;
        ">
            {name}
        </h3>

        <p style="
            color:#64748b;
            margin:10px 0;
        ">
            Code:
            <span style="
                background:#e7f3f1;
                color:#0f766e;
                padding:2px 8px;
                border-radius:5px;
            ">
                {code}
            </span>
        </p>

        <p style="color:#64748b;">
            Section: <b>{section}</b>
        </p>
    """

    if stats:

        html += """
        <div style="
            display:flex;
            gap:8px;
            flex-wrap:wrap;
            margin-top:15px;
        ">
        """

        for icon, label, value in stats:

            html += f"""
            <div style="
                background:#f1f3f2;
                padding:5px 12px;
                border-radius:12px;
                font-size:0.9rem;
            ">
                {icon} <b>{value}</b> {label}
            </div>
            """

        html += "</div>"

    html += "</div>"

    st.html(html)

    if footer_callback:
        footer_callback()
