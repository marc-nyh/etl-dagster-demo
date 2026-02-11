-- Create raw ULD table for incoming data
CREATE TABLE IF NOT EXISTS raw_uld (
  id SERIAL PRIMARY KEY,
  uld_code TEXT
);

-- Create clean ULD table for validated data
CREATE TABLE IF NOT EXISTS clean_uld (
  id INT,
  uld_code TEXT
);

-- Create invalid ULD table for rejected data
CREATE TABLE IF NOT EXISTS invalid_uld (
  id INT,
  uld_code TEXT,
  reason TEXT
);
