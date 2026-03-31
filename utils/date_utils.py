from datetime import datetime

DATE_FORMAT = "%d-%m-%Y"

def normalize_date(value: str) -> str:
    txt = str(value or "").strip()
    if txt == "":
        return ""
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(txt, fmt).strftime(DATE_FORMAT)
        except ValueError:
            pass
    raise ValueError("Data inválida. Use DD-MM-AAAA.")

def parse_date(value: str):
    txt = str(value or "").strip()
    if txt == "":
        return None
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(txt, fmt)
        except ValueError:
            pass
    return None
