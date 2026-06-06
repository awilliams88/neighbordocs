from app import extract_text


def test_extract_text_missing_file() -> None:
    assert extract_text(None) == "No file uploaded."
