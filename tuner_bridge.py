"""
Bridge module for launching Modal fine-tuning runs programmatically.
Spawns the training job in a subprocess and streams remote stdout logs to the Gradio UI.
"""

from __future__ import annotations

import os
import sys
import subprocess
from collections.abc import Generator


def run_ui_fine_tuning(hf_token: str, repo_id: str) -> Generator[str, None, None]:
    """Generator function that invokes Modal fine-tuning and yields logs in real-time.

    Gradio natively renders generator yields as real-time text block updates.
    """
    hf_token = hf_token.strip()
    repo_id = repo_id.strip()

    if not hf_token:
        yield "Error: Hugging Face Access Token is required to authenticate and publish the model."
        return
    if not repo_id or "/" not in repo_id:
        yield "Error: Repository destination must be in the format 'username/repo-name'."
        return

    yield "Starting InnerSpace automated cloud fine-tuning pipeline...\n"
    yield "Connecting to Modal.com serverless GPU cluster...\n"

    # Python code block to execute train_lora.remote() with user-supplied arguments
    python_command = (
        f"import sys; sys.path.insert(0, '.'); "
        f"from tune_journal import train_lora; "
        f"train_lora.remote(hf_token='{hf_token}', repo_id='{repo_id}')"
    )

    try:
        # Launch the python execution as a subprocess, merging stderr into stdout
        process = subprocess.Popen(
            [sys.executable, "-c", python_command],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            # Ensure subprocess inherits the current env (e.g. MODAL_TOKEN_ID/SECRET)
            env=os.environ.copy(),
        )

        accumulated_logs = []
        # Read the subprocess output line by line as it is generated
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                accumulated_logs.append(line)
                yield "".join(accumulated_logs)

        process.wait()
        if process.returncode == 0:
            yield (
                "".join(accumulated_logs)
                + "\n\n🎉 Success! Model fine-tuning and publishing completed successfully."
            )
        else:
            yield (
                "".join(accumulated_logs)
                + f"\n\n❌ Error: Training process terminated with exit code {process.returncode}."
            )

    except Exception as e:
        yield f"Critical Exception: Failed to start training process: {e}"
