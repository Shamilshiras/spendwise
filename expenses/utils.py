from decimal import Decimal, ROUND_HALF_UP


def format_inr(value, show_paise=False):
    if value is None:
        return "₹0"

    try:
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
    except Exception:
        return f"₹{value}"

    is_negative = value < 0
    value = abs(value)

    # Quantize to 2 decimal places
    quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    parts = f"{quantized:.2f}".split(".")
    int_str = parts[0]
    paise_str = parts[1]

    # Indian numbering format grouping:
    # The last 3 digits, followed by groups of 2 digits
    if len(int_str) <= 3:
        formatted_int = int_str
    else:
        last_three = int_str[-3:]
        remaining = int_str[:-3]
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        formatted_int = ",".join(groups) + "," + last_three

    sign = "-" if is_negative else ""

    if show_paise or (paise_str != "00"):
        return f"{sign}₹{formatted_int}.{paise_str}"
    return f"{sign}₹{formatted_int}"
