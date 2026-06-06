from __future__ import annotations

CUSTOM_CSS = """
/* Custom CSS for a premium, clean look */
.gradio-container {
  max-width: 1100px !important;
  margin: 0 auto !important;
  padding: 24px !important;
}

#nd-header {
  text-align: center;
  margin-bottom: 28px;
  padding: 24px;
  background: linear-gradient(135deg, #f0fdfa 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}

#nd-header h1 {
  font-size: 32px;
  font-weight: 800;
  color: #0f172a;
  background: linear-gradient(to right, #0d9488, #0f766e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
}

#nd-header p {
  color: #475569;
  font-size: 16px;
  font-weight: 500;
}

.nd-btn {
  background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%) !important;
  color: white !important;
  font-weight: 600 !important;
  border: none !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 6px -1px rgba(13, 148, 136, 0.2) !important;
  transition: all 0.2s ease-in-out !important;
}

.nd-btn:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 10px 15px -3px rgba(13, 148, 136, 0.3) !important;
}

.nd-output-box textarea {
  font-family: ui-sans-serif, system-ui, sans-serif !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  border-radius: 8px !important;
}

.nd-log-box textarea {
  font-family: 'Courier New', Courier, monospace !important;
  font-size: 13px !important;
  background-color: #0f172a !important;
  color: #38bdf8 !important;
  border-radius: 8px !important;
}

#nd-links {
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
  font-size: 14px;
}

#nd-links a {
  color: #0d9488;
  text-decoration: none;
  font-weight: 600;
}

#nd-links a:hover {
  text-decoration: underline;
}
"""
