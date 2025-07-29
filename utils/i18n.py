import gettext
import os
from functools import lru_cache


@lru_cache(maxsize=None)
def get_translator(language: str = "en") -> gettext.NullTranslations:
    """Return a cached gettext translation object for the specified language.

    This function loads and caches the translation object for the given language code.
    It extracts the language prefix (e.g., 'en' from 'en_US') and looks for translation
    files under the 'languages' directory next to the current file.

    Args:
        language (str): Language code, e.g., 'en', 'fa'. Defaults to environment variable 'DEFAULT_LANG'.

    Returns:
        gettext.NullTranslations: The translation object. Falls back to a null translation if no files found.
    """
    try:
        return gettext.translation(
            domain="messages",
            localedir=os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "languages")
            ),
            languages=[language.split("_")[0]],
            fallback=True,
        )
    except Exception:
        return gettext.NullTranslations()


_ = get_translator().gettext
