-- ============================================================
-- Financial Assistant — Real Estate Corp
-- seed_data.sql
-- Populates properties and financials with sample data
-- Run after create_tables.sql
-- ============================================================

-- ------------------------------------------------------------
-- Properties
-- ------------------------------------------------------------
INSERT INTO properties (property_name, address, metro_area, property_type, square_footage, year_built) VALUES
-- Chicago — Industrial (referenced in press release: acquisition of 5 industrial properties)
('Chicago Logistics Hub A',     '1200 Industrial Pkwy, Chicago, IL 60601',       'Chicago', 'industrial', 120000, 2010),
('Chicago Logistics Hub B',     '1350 Industrial Pkwy, Chicago, IL 60601',       'Chicago', 'industrial',  98000, 2012),
('Chicago Distribution Center', '4500 West Freight Blvd, Chicago, IL 60632',     'Chicago', 'industrial', 210000, 2008),
('Chicago Warehouse Complex',   '7800 South Logistics Dr, Chicago, IL 60638',    'Chicago', 'industrial', 175000, 2015),
('Chicago Commerce Park',       '2200 North Commerce Ave, Chicago, IL 60614',    'Chicago', 'industrial',  88000, 2018),

-- Miami — Office (referenced in press release: expansion into Miami office market)
('Miami Tower One',             '100 Brickell Ave, Miami, FL 33131',             'Miami',   'office',      95000, 2016),
('Miami Bay Class A',           '250 Biscayne Blvd, Miami, FL 33132',            'Miami',   'office',     110000, 2019),

-- Additional cities for filter variety
('Dallas Retail Plaza',         '500 Commerce St, Dallas, TX 75201',             'Dallas',  'retail',      62000, 2011),
('Dallas Office Park',          '1800 Main St, Dallas, TX 75201',                'Dallas',  'office',      78000, 2014),
('Phoenix Industrial Park',     '3300 East Van Buren St, Phoenix, AZ 85008',     'Phoenix', 'industrial', 145000, 2017),
('Phoenix Retail Center',       '9900 North Metro Pkwy, Phoenix, AZ 85051',      'Phoenix', 'retail',      55000, 2013),
('New York Office Tower',       '350 Fifth Ave, New York, NY 10118',             'New York','office',     200000, 2005),
('New York Retail Block',       '680 Madison Ave, New York, NY 10065',           'New York','retail',      40000, 2009),
('Los Angeles Industrial',      '2100 East 25th St, Los Angeles, CA 90058',      'Los Angeles', 'industrial', 130000, 2016),
('Los Angeles Office Hub',      '633 West 5th St, Los Angeles, CA 90071',        'Los Angeles', 'office',   115000, 2012),

-- Seattle and Boston for additional variety (bringing total to 20)
('Seattle Tech Campus',         '1301 Fifth Ave, Seattle, WA 98101',             'Seattle',     'office',    88000, 2017),
('Seattle Industrial Port',     '2800 East Marginal Way, Seattle, WA 98134',     'Seattle',     'industrial',160000, 2014),
('Boston Financial Center',     '100 Federal St, Boston, MA 02110',              'Boston',      'office',    125000, 2011),
('Boston Retail Row',           '330 Newbury St, Boston, MA 02115',              'Boston',      'retail',     48000, 2010),
('Boston Warehouse District',   '15 Channel Center St, Boston, MA 02210',        'Boston',      'industrial', 95000, 2016);


-- ------------------------------------------------------------
-- Financials (fiscal year 2024)
-- net_income is auto-calculated as revenue - expenses
-- ------------------------------------------------------------
INSERT INTO financials (property_id, fiscal_year, revenue, expenses) VALUES
-- Chicago Industrial
(1,  2024, 4800000.00, 2100000.00),
(2,  2024, 3900000.00, 1750000.00),
(3,  2024, 8200000.00, 3600000.00),
(4,  2024, 6900000.00, 3100000.00),
(5,  2024, 3500000.00, 1600000.00),

-- Miami Office
(6,  2024, 5100000.00, 2300000.00),
(7,  2024, 5900000.00, 2600000.00),

-- Dallas
(8,  2024, 2800000.00, 1300000.00),
(9,  2024, 3600000.00, 1650000.00),

-- Phoenix
(10, 2024, 5700000.00, 2500000.00),
(11, 2024, 2200000.00, 1050000.00),

-- New York
(12, 2024, 9800000.00, 4200000.00),
(13, 2024, 2100000.00,  980000.00),

-- Los Angeles
(14, 2024, 5300000.00, 2400000.00),
(15, 2024, 5600000.00, 2500000.00),

-- Seattle
(16, 2024, 4200000.00, 1900000.00),
(17, 2024, 6100000.00, 2700000.00),

-- Boston
(18, 2024, 5800000.00, 2600000.00),
(19, 2024, 2400000.00, 1100000.00),
(20, 2024, 3800000.00, 1700000.00);
