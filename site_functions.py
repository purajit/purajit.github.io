"""Custom helpers available to every template.

Any public function defined here can be called from a Jinja template, e.g.
``{{ romanize(3) }}``.
"""


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
