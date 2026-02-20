-- Remove the old tables if it's there
DROP TABLE IF EXISTS raw_uld;
DROP TABLE IF EXISTS clean_uld;
DROP TABLE IF EXISTS invalid_uld;
DROP TABLE IF EXISTS enriched_uld;

-- Create raw ULD table for incoming data
CREATE TABLE raw_uld (
  id SERIAL PRIMARY KEY,
  uld_code TEXT
);

-- Create clean ULD table for validated data
CREATE TABLE clean_uld (
  id INT,
  uld_code TEXT
);

-- Create invalid ULD table for rejected data
CREATE TABLE invalid_uld (
  id INT,
  uld_code TEXT,
  reason TEXT
);

-- Create enriched ULD table for validated data with Airline info
CREATE TABLE enriched_uld (
  id INT,
  uld_code TEXT,
  airline_code TEXT,
  airline_name TEXT
);

