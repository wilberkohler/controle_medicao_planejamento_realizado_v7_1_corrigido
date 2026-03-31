def to_float(value) -> float:
    txt = str(value or "").strip()
    if txt == "":
        return 0.0
    txt = txt.replace(".", "").replace(",", ".")
    return float(txt)

def to_int(value) -> int:
    txt = str(value or "").strip()
    if txt == "":
        return 0
    txt = txt.replace(",", ".")
    return int(float(txt))

def br_number(value, decimals=2) -> str:
    try:
        return f"{float(value or 0):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(value)
