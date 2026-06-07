from __future__ import annotations

# Gradio CSS overrides keep the app visually distinct for Off-Brand judging.
CUSTOM_CSS = """
body, .gradio-container {
    background-color: #0c0e17 !important;
    color: #e2e8f0 !important;
    font-family: "Outfit", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}


/* Header and product kicker */
#nd-header {
    text-align: center;
    margin: 0 auto 0.75rem auto;
    padding: 0.35rem 0 0.75rem 0;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
#nd-header h1 {
    color: #c084fc !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0 !important;
    margin-bottom: 0.35rem !important;
}
#nd-header p {
    color: #94a3b8 !important;
    font-size: 1.15rem !important;
    margin: 0 !important;
}
#nd-kicker {
    width: fit-content;
    max-width: 90%;
    margin: 0 auto 2rem auto;
    padding: 0.75rem 2.25rem !important;
    background: transparent !important;
    border: 2px solid #c084fc !important;
    box-shadow: none !important;
    text-align: center;
    color: #c7d2fe !important;
    font-size: 1.1rem !important;
    line-height: 1.6 !important;
    border-radius: 40px !important;
}
#nd-journal-input textarea {
    min-height: 200px !important;
    resize: vertical !important;
}

/* Main panels */
.nd-main-grid {
    gap: 1.25rem !important;
    align-items: stretch !important;
}
.nd-input-panel, .nd-output-panel, .nd-analysis-section {
    background-color: #151829 !important;
    border: 1px solid #2d2e4a !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
    padding: 1.25rem !important;
}
.nd-analysis-section {
    margin-top: 1.25rem !important;
}
.nd-output-panel {
    display: flex !important;
    flex-direction: column !important;
}
.nd-input-panel h3, .nd-output-panel h3, .nd-analysis-section h3 {
    margin: 0 0 0.8rem 0 !important;
    color: #e2e8f0 !important;
}
.nd-input-panel h3, .nd-output-panel h3 {
    font-size: 1.05rem !important;
}
.nd-analysis-section h3 {
    font-size: 1.20rem !important;
    border-bottom: 1px solid #2d2e4a;
    padding-bottom: 0.5rem;
}

/* Output text areas */
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

/* Chat controls */
.nd-chatbot {
    background-color: #110e20 !important;
    border: 1px solid #3b1b63 !important;
    border-radius: 8px !important;
    flex: 1 1 auto !important;
    min-height: 280px !important;
    overflow: hidden !important;
}
.nd-chatbot > div {
    height: 100% !important;
    max-height: 100% !important;
}
.nd-chatbot .message, .nd-chatbot .bubble, .nd-chatbot .prose {
    line-height: 1.45 !important;
    overflow-wrap: anywhere !important;
}
.nd-chatbot .prose {
    max-width: 100% !important;
}

.nd-chat-row {
    align-items: center !important;
    gap: 0.8rem !important;
    margin: 0.8rem 0 1rem 0 !important;
}
.nd-chat-row > div:first-child {
    flex: 1 1 auto !important;
}
.nd-chat-row > div:last-child {
    display: flex !important;
    align-items: center !important;
    flex: 0 0 150px !important;
}
.nd-chat-input {
    min-width: 0 !important;
}
.nd-chat-input textarea {
    background-color: #0c0e17 !important;
    color: #f1f5f9 !important;
    border: 1px solid #2d2e4a !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
    min-height: 52px !important;
    max-height: 92px !important;
    padding: 0.8rem 0.9rem !important;
}
.nd-send-btn {
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
    min-height: 52px !important;
    align-self: center !important;
}
.nd-send-btn:hover {
    opacity: 0.9 !important;
}

/* Summary cards */
.nd-card-grid {
    gap: 1rem !important;
    align-items: stretch !important;
    margin-top: 0.85rem !important;
}
.nd-output-card {
    min-width: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.nd-card-grid > .form, .nd-card-grid > .row, .nd-card-grid > div {
    display: flex !important;
    gap: 1.25rem !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.nd-card-grid .block {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    flex: 1 1 0% !important;
}
.nd-output-card textarea {
    font-family: inherit !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    padding: 0.75rem !important;
    border-radius: 8px !important;
    min-height: 110px !important;
    overflow: auto !important;
}

/* Card color accents */
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
.nd-reframe-card textarea {
    border: 1px solid rgba(14, 165, 233, 0.4) !important;
    background-color: rgba(14, 165, 233, 0.05) !important;
    color: #bae6fd !important;
}
.nd-next-step-card textarea {
    border: 1px solid rgba(245, 158, 11, 0.4) !important;
    background-color: rgba(245, 158, 11, 0.06) !important;
    color: #fde68a !important;
}

/* Diagnostics */
.nd-log-box textarea {
    background-color: #05060f !important;
    color: #a78bfa !important;
    border: 1px solid #2d2e4a !important;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace !important;
    font-size: 0.9rem !important;
}

/* Primary action */
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
    width: 100% !important;
    min-height: 48px !important;
}
.nd-btn:hover {
    opacity: 0.95 !important;
    transform: translateY(-1px) !important;
}
.nd-btn:active {
    transform: translateY(0px) !important;
}

/* Footer links */
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



/* Custom styling for labels to remove excessive purple */
.gradio-container label span, .gradio-container .nd-slider span {
    background-color: #272a44 !important;
    color: #cbd5e1 !important;
    border: 1px solid #3b3f66 !important;
}

/* Specific card label accents matching their card theme */
.nd-emotions-card label span {
    background-color: rgba(124, 58, 237, 0.25) !important;
    color: #c7d2fe !important;
    border: 1px solid rgba(124, 58, 237, 0.5) !important;
}
.nd-areas-card label span {
    background-color: rgba(16, 185, 129, 0.25) !important;
    color: #a7f3d0 !important;
    border: 1px solid rgba(16, 185, 129, 0.5) !important;
}
.nd-distortions-card label span {
    background-color: rgba(239, 68, 68, 0.25) !important;
    color: #fca5a5 !important;
    border: 1px solid rgba(239, 68, 68, 0.5) !important;
}
.nd-reframe-card label span {
    background-color: rgba(14, 165, 233, 0.25) !important;
    color: #bae6fd !important;
    border: 1px solid rgba(14, 165, 233, 0.5) !important;
}
.nd-next-step-card label span {
    background-color: rgba(245, 158, 11, 0.25) !important;
    color: #fde68a !important;
    border: 1px solid rgba(245, 158, 11, 0.5) !important;
}
"""
