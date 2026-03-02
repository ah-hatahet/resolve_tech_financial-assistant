-- ============================================================
-- Financial Assistant — Real Estate Corp
-- create_tables.sql
-- Creates the properties and financials tables in PostgreSQL
-- ============================================================

-- Drop tables if they already exist (for clean re-runs)
DROP TABLE IF EXISTS financials;
DROP TABLE IF EXISTS properties;

-- ------------------------------------------------------------
-- Properties table
-- Stores core information about each real estate asset
-- ------------------------------------------------------------
CREATE TABLE properties (
    property_id     SERIAL PRIMARY KEY,
    property_name   VARCHAR(255)   NOT NULL,
    address         VARCHAR(255),
    metro_area      VARCHAR(100)   NOT NULL,
    property_type   VARCHAR(50)    NOT NULL,  -- e.g. industrial, office, retail
    square_footage  INTEGER,
    year_built      INTEGER
);

-- ------------------------------------------------------------
-- Financials table
-- Stores annual financial performance per property
-- ------------------------------------------------------------
CREATE TABLE financials (
    financial_id    SERIAL PRIMARY KEY,
    property_id     INTEGER        NOT NULL REFERENCES properties(property_id) ON DELETE CASCADE,
    fiscal_year     INTEGER        NOT NULL,
    revenue         NUMERIC(15, 2) NOT NULL,
    expenses        NUMERIC(15, 2) NOT NULL,
    net_income      NUMERIC(15, 2) GENERATED ALWAYS AS (revenue - expenses) STORED
);

-- Indexes for common query patterns
CREATE INDEX idx_properties_metro_area    ON properties(metro_area);
CREATE INDEX idx_properties_property_type ON properties(property_type);
CREATE INDEX idx_financials_property_id   ON financials(property_id);
CREATE INDEX idx_financials_fiscal_year   ON financials(fiscal_year);
