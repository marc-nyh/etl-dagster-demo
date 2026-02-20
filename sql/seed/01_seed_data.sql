-- Seed raw ULD data for testing
-- Test cases:
--   1. Valid 2-letter owner code (lowercase -> will be uppercased)
--   2. Valid 3-letter owner code (DHL)
--   3. Spaced ULD -> repaired (space between type+serial)
--   4. Spaced ULD -> repaired (space before owner code)
--   5. Spaced ULD -> still invalid after repair (wrong structure)
--   6. Genuinely invalid format

INSERT INTO raw_uld (uld_code) VALUES
('ake12345sq'),          -- Valid (2-letter): becomes AKE12345SQ
('AKE12345DHL'),         -- Valid (3-letter): DHL Aviation
('AKE 12345SQ'),         -- Repairable: space mid-code -> AKE12345SQ
('PMC 67890 MH'),        -- Repairable: spaces -> PMC67890MH
('LD3 1234 AKE'),        -- NOT repairable: wrong structure (no 5-digit serial)
('BADCODE');             -- NOT repairable: completely wrong format
