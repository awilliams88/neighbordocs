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

/* Chatbot container customization */
.nd-chatbot {
    background-color: #110e20 !important;
    border: 1px solid #3b1b63 !important;
    border-radius: 12px !important;
}

/* Chat text input and buttons */
.nd-chat-input textarea {
    background-color: #0c0e17 !important;
    color: #f1f5f9 !important;
    border: 1px solid #2d2e4a !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
}
.nd-send-btn {
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.nd-send-btn:hover {
    opacity: 0.9 !important;
}

/* Glassmorphic dashboard cards styling */
.nd-output-card textarea {
    font-family: inherit !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    padding: 0.75rem !important;
    border-radius: 8px !important;
}

/* Specific card styles */
.nd-emotions-card textarea {
    border: 1px solid rgba(124, 58, 237, 0.4) !important;
    background-color: rgba(124, 58, 237, 0.05) !important;
    color: #c7d2fe !important;
}
.nd-areas-card textarea {
    border: 1px solid rgba(16, 185, 129, 0.4) !important;
    background-color: rgba(16, 185, 129, 0.05) !important;
    color: #a7f3d0 !important;
}
.nd-distortions-card textarea {
    border: 1px solid rgba(239, 68, 68, 0.4) !important;
    background-color: rgba(239, 68, 68, 0.05) !important;
    color: #fca5a5 !important;
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
