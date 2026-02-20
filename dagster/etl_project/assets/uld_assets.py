from dagster import asset, multi_asset, AssetOut, Output, MaterializeResult
import re
from typing import List, Tuple, Any
from ..resources import PostgresResource

# --- Constants ---

# Updated to support 2 OR 3 letter owner codes (e.g. SQ, DHL)
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

# --- Assets ---

# 1. Extract
@asset
def raw_uld_records(database: PostgresResource) -> List[Tuple[int, str]]:
    """Extracts raw ULD records from PostgreSQL."""
    conn = database.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, uld_code FROM raw_uld")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

# 2. Splitter (Fork)
# @multi_asset: one function, two output assets (valid_records and invalid_records)
@multi_asset(
    outs={
        "valid_records": AssetOut(),
        "invalid_records": AssetOut()
    }
)
def validated_uld_records(raw_uld_records: List[Tuple[int, str]]):
    """Classifies ULD records and splits them into two streams."""
    valid = []
    invalid = []

    for id_, code in raw_uld_records:
        if not code:
            continue

        cleaned = code.strip().upper()

        if ULD_PATTERN.match(cleaned):
            valid.append((id_, cleaned))
        else:
            invalid.append((id_, cleaned, "Invalid ULD format"))

    yield Output(valid, "valid_records")
    yield Output(invalid, "invalid_records")

# 3. Branch A: Process Valid (Enrich & Load)
@asset
def process_valid_records(database: PostgresResource, valid_records: List[Tuple[int, str]]):
    """Enriches valid records with airline info and saves to clean_uld and enriched_uld."""
    enriched = []
    for id_, code in valid_records:
        # Owner code = everything after the first 8 chars (3 type letters + 5 digits)
        # Handles both 2-letter (SQ) and 3-letter (DHL) codes
        owner_code = code[8:]
        airline_name = AIRLINE_CODES.get(owner_code, "Unknown Airline")
        # Schema: id, uld_code, airline_code, airline_name, original_code, action_taken
        enriched.append((id_, code, owner_code, airline_name, code, "Valid"))

    conn = database.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM clean_uld")
        cur.execute("DELETE FROM enriched_uld")

        if valid_records:
            cur.executemany(
                "INSERT INTO clean_uld (id, uld_code) VALUES (%s, %s)",
                valid_records,
            )

        if enriched:
            cur.executemany(
                "INSERT INTO enriched_uld (id, uld_code, airline_code, airline_name, original_code, action_taken)"
                " VALUES (%s, %s, %s, %s, %s, %s)",
                enriched,
            )
        conn.commit()
        return len(enriched)
    finally:
        cur.close()
        conn.close()

# 4. Branch B: Process Invalid (Auto-Repair & Load)
@asset
def process_invalid_records(database: PostgresResource, invalid_records: List[Tuple[int, str, str]]):
    """
    Attempts to repair invalid records by removing spaces.
    - If repaired code is valid → saves to enriched_uld with action_taken='Repaired'.
    - Otherwise → saves to invalid_uld.
    """
    repaired_records = []
    truly_invalid_records = []

    for id_, code, reason in invalid_records:
        # Attempt repair: strip all spaces
        fixed_code = code.replace(" ", "").upper()

        if ULD_PATTERN.match(fixed_code):
            # It's now valid! Enrich it.
            owner_code = fixed_code[8:]
            airline_name = AIRLINE_CODES.get(owner_code, "Unknown Airline")
            # original_code = original (with spaces), action_taken = note about repair
            repaired_records.append(
                (id_, fixed_code, owner_code, airline_name, code, "Repaired: Removed Spaces")
            )
        else:
            truly_invalid_records.append((id_, code, reason))

    conn = database.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM invalid_uld")

        # Repaired records go into enriched_uld (they are now valid!)
        if repaired_records:
            cur.executemany(
                "INSERT INTO enriched_uld (id, uld_code, airline_code, airline_name, original_code, action_taken)"
                " VALUES (%s, %s, %s, %s, %s, %s)",
                repaired_records,
            )

        # Truly invalid records go into invalid_uld
        if truly_invalid_records:
            cur.executemany(
                "INSERT INTO invalid_uld (id, uld_code, reason) VALUES (%s, %s, %s)",
                truly_invalid_records,
            )
        conn.commit()
        # Return a dict so the summary can show the breakdown
        return {
            "repaired": len(repaired_records),
            "truly_invalid": len(truly_invalid_records)
        }
    finally:
        cur.close()
        conn.close()

# 5. Join: Summary Report
@asset
def uld_processing_summary(process_valid_records: int, process_invalid_records: dict):
    """Aggregates results from both branches into a visible metadata report."""
    repaired = process_invalid_records["repaired"]
    truly_invalid = process_invalid_records["truly_invalid"]
    total_valid = process_valid_records
    total_processed = total_valid + repaired + truly_invalid

    return MaterializeResult(
        metadata={
            "status": "Success",
            "total_valid": total_valid,
            "total_auto_corrected": repaired,       # Was invalid but fixed by removing spaces
            "total_truly_invalid": truly_invalid,   # Could not be fixed
            "total_processed": total_processed,
        }
    )
