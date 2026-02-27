import re

# Example ULD codes: [AKN 12345 DL]
ULD_PATTERN = re.compile(r"^[A-Z]{3}[0-9]{5}[A-Z]{2,3}$")

AIRLINE_CODES = {
    "SQ": "Singapore Airlines",
    "MH": "Malaysia Airlines",
    "CX": "Cathay Pacific",
    "EK": "Emirates",
    "UA": "United Airlines",
    "BA": "British Airways",
    "QF": "Qantas",
    "DHL": "DHL Aviation",   # 3-letter code
}