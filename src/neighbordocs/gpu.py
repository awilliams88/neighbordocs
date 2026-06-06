from __future__ import annotations

from collections.abc import Callable

try:
    import spaces
except ImportError:

    class _LocalSpacesFallback:
        @staticmethod
        def GPU(
            duration: int = 30,
        ) -> Callable[[Callable[..., str]], Callable[..., str]]:
            def decorator(function: Callable[..., str]) -> Callable[..., str]:
                return function

            return decorator

    spaces = _LocalSpacesFallback()


@spaces.GPU(duration=30)
def run_zero_gpu_document_path(model_label: str, preview: str) -> str:
    if not preview or preview == "No file uploaded.":
        return "ZeroGPU path: upload a document before running the GPU model path."

    return "\n".join(
        [
            "ZeroGPU path: ready for model-backed document inference.",
            f"Selected model strategy: {model_label}",
            "Current release: the GPU hook is wired and Gradio-callable; the public Space remains CPU until the final model integration is attached.",
            "Next integration target: document parser or <=4B reasoner inside this decorated function.",
        ]
    )
