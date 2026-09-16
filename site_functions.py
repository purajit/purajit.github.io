"""Custom helpers available to every template.

Any public function defined here can be called from a Jinja template, e.g.
``{{ romanize(3) }}``. They are also imported by ``fetch_assets.py`` so the
asset filenames stay in sync with what the templates request.
"""

import re


def slugify(text: str) -> str:
    """Turn a title into a url/filename-safe slug (``A Title!`` -> ``a-title``)."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def romanize(number: int) -> str:
    conversions = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    result = ""
    for value, numeral in conversions:
        result += numeral * (number // value)
        number %= value
    return result
