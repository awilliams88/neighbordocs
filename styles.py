from __future__ import annotations

# Custom CSS targeting premium dark violet mindfulness theme (inspired by meditation and journaling tools)
CUSTOM_CSS = """
body, .gradio-container {
    background-color: #0c0e17 !important;
    color: #e2e8f0 !important;
    font-family: "Outfit", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}

/* Header customization */
#nd-header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #2d2e4a;
}
#nd-header h1 {
    color: #c084fc !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
}
#nd-header p {
    color: #94a3b8 !important;
    font-size: 1.15rem !important;
}

/* Panel and card customization */
.gradio-container .block, .gradio-container .panel {
    background-color: #151829 !important;
    border: 1px solid #2d2e4a !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
}

/* TextBox output fields styling */
.nd-output-box textarea {
    background-color: #0c0e17 !important;
    color: #f1f5f9 !important;
    border: 1px solid #2d2e4a !important;
    border-radius: 8px !important;
    font-family: inherit !important;
    font-size: 1.05rem !important;
    line-height: 1.6 !important;
    padding: 1rem !important;
}

/* Highlighted Reflective Coach question box */
.nd-coach-box textarea {
    background-color: #1d193b !important;
    color: #e9d5ff !important;
    border: 1px solid #6b21a8 !important;
    font-weight: 500 !important;
}

/* Red highlighted Cognitive Distortion warning fields */
.nd-distortions-box textarea {
    background-color: #24141d !important;
    color: #fca5a5 !important;
    border: 1px solid #991b1b !important;
}

/* System console style output box */
.nd-log-box textarea {
    background-color: #05060f !important;
    color: #a78bfa !important;
    border: 1px solid #2d2e4a !important;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace !important;
    font-size: 0.9rem !important;
}

/* Calming Violet Action Button */
.nd-btn {
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 1.1rem !important;
    transition: transform 0.15s ease, opacity 0.15s ease !important;
    box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.3) !important;
}
.nd-btn:hover {
    opacity: 0.95 !important;
    transform: translateY(-1px) !important;
}
.nd-btn:active {
    transform: translateY(0px) !important;
}

/* Footer links alignment */
#nd-links {
    text-align: center;
    margin-top: 2.5rem;
    color: #94a3b8 !important;
}
#nd-links a {
    color: #c084fc !important;
    text-decoration: none !important;
    font-weight: 500 !important;
}
#nd-links a:hover {
    text-decoration: underline !important;
}
"""
