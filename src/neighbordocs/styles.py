from __future__ import annotations

CUSTOM_CSS = """
:root {
  --nd-ink: #1f2933;
  --nd-muted: #52606d;
  --nd-line: #d9e2ec;
  --nd-panel: #f8fafc;
  --nd-accent: #0f766e;
  --nd-accent-dark: #115e59;
}

.gradio-container {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--nd-ink);
}

#nd-header {
  border-bottom: 1px solid var(--nd-line);
  margin-bottom: 14px;
  padding-bottom: 12px;
}

#nd-header h1 {
  font-size: 34px;
  line-height: 1.1;
  margin-bottom: 8px;
}

#nd-header p {
  color: var(--nd-muted);
  font-size: 15px;
  margin: 0;
}

.nd-panel {
  background: var(--nd-panel);
  border: 1px solid var(--nd-line);
  border-radius: 8px;
}

.nd-action button {
  background: var(--nd-accent) !important;
  border-color: var(--nd-accent) !important;
}

.nd-action button:hover {
  background: var(--nd-accent-dark) !important;
  border-color: var(--nd-accent-dark) !important;
}

#nd-links {
  border-top: 1px solid var(--nd-line);
  color: var(--nd-muted);
  margin-top: 10px;
  padding-top: 12px;
}
"""
