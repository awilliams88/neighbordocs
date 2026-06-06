from __future__ import annotations

CUSTOM_CSS = """
/* Codex/GitHub Dark Theme CSS */
body, html, .gradio-container {
  background-color: #0d1117 !important;
  color: #c9d1d9 !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji" !important;
}

#nd-header {
  text-align: center;
  margin-bottom: 24px;
  padding: 24px;
  background-color: #161b22;
  border-radius: 6px;
  border: 1px solid #30363d;
}

#nd-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #f0f6fc;
  margin-bottom: 6px;
}

#nd-header p {
  color: #8b949e;
  font-size: 15px;
}

/* Make inputs and output panels look like GitHub dark cards */
.gradio-container .block, .gradio-container .form {
  background-color: #161b22 !important;
  border: 1px solid #30363d !important;
  border-radius: 6px !important;
}

.gradio-container input, .gradio-container textarea, .gradio-container select {
  background-color: #0d1117 !important;
  color: #c9d1d9 !important;
  border: 1px solid #30363d !important;
  border-radius: 6px !important;
}

.gradio-container input:focus, .gradio-container textarea:focus {
  border-color: #58a6ff !important;
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3) !important;
}

/* Customize Button to GitHub Green Button */
.nd-btn {
  background-color: #238636 !important;
  color: #ffffff !important;
  font-weight: 500 !important;
  border: 1px solid rgba(240, 246, 252, 0.1) !important;
  border-radius: 6px !important;
  transition: background-color 0.2s !important;
}

.nd-btn:hover {
  background-color: #2ea44f !important;
}

/* Terminal Log Box */
.nd-log-box textarea {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
  font-size: 13px !important;
  background-color: #010409 !important;
  color: #58a6ff !important;
  border-radius: 6px !important;
}

.nd-output-box textarea {
  color: #f0f6fc !important;
}

/* Links */
#nd-links {
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #30363d;
  font-size: 13px;
  color: #8b949e;
}

#nd-links a {
  color: #58a6ff;
  text-decoration: none;
}

#nd-links a:hover {
  text-decoration: underline;
}

/* Gradio Tabs Styling */
.tabs {
  border-bottom: 1px solid #30363d !important;
}

.tab-nav button {
  color: #8b949e !important;
  border-bottom: 2px solid transparent !important;
}

.tab-nav button.selected {
  color: #f0f6fc !important;
  border-bottom-color: #f78166 !important; /* GitHub tab accent color */
}
"""
