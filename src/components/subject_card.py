from html import escape

import streamlit as st


def subject_card(
    name,
    code,
    section,
    stats=None,
    footer_callback=None,
    progress=None,
    status=None,
):

    name = escape(str(name))
    code = escape(str(code))
    section = escape(str(section))

    safe_status = escape(str(status)) if status else None
    status_class = (
        "iq-status-good"
        if safe_status == "Good standing"
        else "iq-status-neutral"
        if safe_status == "No records"
        else "iq-status-risk"
    )
    status_html = (
        f'<span class="iq-status-badge {status_class}">{safe_status}</span>'
        if safe_status
        else ""
    )
    html = f"""
    <div class="iq-subject-card">
        <div class="iq-subject-top">
            <div><h3>{name}</h3><div class="iq-subject-meta">{code} · Section {section}</div></div>
            {status_html}
        </div>
    """

    if stats:

        html += '<div class="iq-subject-stats">'

        for icon, label, value in stats:

            html += (
                '<div class="iq-subject-stat">'
                f'<span>{escape(str(label))}</span><strong>{escape(str(value))}</strong>'
                '</div>'
            )

        html += "</div>"

    if progress is not None:
        progress_value = max(0.0, min(100.0, float(progress)))
        html += f"""
        <div class="iq-progress"><span style="width:{progress_value:.1f}%"></span></div>
        <div class="iq-subject-progress-label">
            <span>Attendance progress</span><strong>{progress_value:.0f}%</strong>
        </div>
        """

    html += "</div>"

    st.html(html)

    if footer_callback:
        footer_callback()
