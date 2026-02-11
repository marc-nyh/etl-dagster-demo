-- Seed raw ULD data for testing
-- Includes various test cases:
--   - Valid ULD codes (lowercase, uppercase)
--   - Invalid formats
--   - Leading/trailing whitespace

INSERT INTO raw_uld (uld_code) VALUES
('ake12345sq'),      -- Valid: lowercase
(' PMC67890'),       -- Invalid: leading space
('ld31234ake'),      -- Invalid: wrong format
('BADCODE');         -- Invalid: not a valid ULD format
