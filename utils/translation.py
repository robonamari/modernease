import os
from typing import Any, Dict

import yaml


async def load_translation(language: str) -> Dict[str, Any]:
    """
    Load the translation file for the given language.

    Args:
        language (str): Language code (e.g., 'en').

    Returns:
        Dict[str, Any]: Dictionary with translation data.

    Raises:
        ValueError: If the file path is invalid.
        FileNotFoundError: If the translation file does not exist.
    """
    base_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "languages")
    )
    file_path = os.path.abspath(os.path.join(base_path, f"{language}.yml"))
    if not file_path.startswith(base_path):
        raise ValueError("Invalid translation file path")
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    raise FileNotFoundError(f"Translation file not found: languages/{language}.yml")
