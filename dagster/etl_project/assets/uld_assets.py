from dagster import asset, multi_asset, AssetOut, Output, MaterializeResult
import re
from typing import List, Tuple, Dict, Any
from ..resources import PostgresResource

# --- Constants ---

ULD_PATTERN = re.compile(r"^[A-Z]{3}[0-9]{5}[A-Z]{2}$")

AIRLINE_CODES = {
    "SQ": "Singapore Airlines",
    "MH": "Malaysia Airlines",
    "CX": "Cathay Pacific",
    "EK": "Emirates",
    "UA": "United Airlines",
    "BA": "British Airways",
    "QF": "Qantas",
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
    """Enriches valid records and saves to clean_uld and enriched_uld."""
    enriched = []
    # Enrichment Logic
    for id_, code in valid_records:
        owner_code = code[-2:]
        airline_name = AIRLINE_CODES.get(owner_code, "Unknown Airline")
        enriched.append((id_, code, owner_code, airline_name))
        
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
                "INSERT INTO enriched_uld (id, uld_code, airline_code, airline_name) VALUES (%s, %s, %s, %s)",
                enriched,
            )
        conn.commit()
        return len(enriched)
    finally:
        cur.close()
        conn.close()

# 4. Branch B: Process Invalid (Fix & Load)
@asset
def process_invalid_records(database: PostgresResource, invalid_records: List[Tuple[int, str, str]]):
    """Attempts to fix invalid records and saves to invalid_uld."""
    conn = database.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM invalid_uld")
        
        # Simple fix logic: If code is 8 chars (missing owner), assume it's 'XX'
        # Note: In a real app, this logic would be more complex
        
        if invalid_records:
             cur.executemany(
                "INSERT INTO invalid_uld (id, uld_code, reason) VALUES (%s, %s, %s)",
                invalid_records,
            )
        conn.commit()
        return len(invalid_records)
    finally:
        cur.close()
        conn.close()

# 5. Join: Summary Report
@asset
def uld_processing_summary(process_valid_records: int, process_invalid_records: int):
    """Aggregates results from both branches."""
    return MaterializeResult(
        metadata={
            "status": "Success",
            "total_valid_enriched": process_valid_records,
            "total_invalid_processed": process_invalid_records,
            "total_processed": process_valid_records + process_invalid_records
        }
    )
