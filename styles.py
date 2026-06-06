from __future__ import annotations

# Custom CSS targeting premium dark theme styling (inspired by GitHub and Codex IDE)
CUSTOM_CSS = """
body, .gradio-container {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
}

/* Header customization */
#nd-header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #30363d;
}
#nd-header h1 {
    color: #58a6ff !important;
    font-size: 2.5rem !important;
    font-weight: 600 !important;
}
#nd-header p {
    color: #8b949e !important;
    font-size: 1.1rem !important;
}

/* Panel and card customization */
.gradio-container .block, .gradio-container .panel {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
}

/* TextBox output fields */
.nd-output-box textarea {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    border: 1px solid #30363d !important;
    font-family: inherit !important;
}

/* Console logs style output box */
.nd-log-box textarea {
    background-color: #010409 !important;
    color: #7ee787 !important;
    border: 1px solid #30363d !important;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace !important;
    font-size: 0.9rem !important;
}

/* GitHub style Green Action Button */
.nd-btn {
    background: #238636 !important;
    color: #ffffff !important;
    border: 1px solid #2ea44f !important;
    font-weight: 600 !important;
    transition: background-color 0.2s !important;
}
.nd-btn:hover {
    background: #2ea44f !important;
}

/* Footer links alignment */
#nd-links {
    text-align: center;
    margin-top: 2rem;
    color: #8b949e !important;
}
#nd-links a {
    color: #58a6ff !important;
    text-decoration: none !important;
}
#nd-links a:hover {
    text-decoration: underline !important;
}
"""
