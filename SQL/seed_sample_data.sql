-- Sample Data Seeding Script for Mechanic Shop V4
-- Run this after running flask db upgrade to populate database with test data

USE mechanic_shop_v4;

-- Note: All test accounts use password 'password123'
-- Password hash generated with werkzeug (scrypt): Compatible with application's password checking

-- Sample Customers
INSERT INTO customers (first_name, last_name, email, phone, address, city, state, postal_code, password_hash) VALUES
('Alice', 'Johnson', 'alice.johnson@email.com', '555-1001', '123 Main St', 'Denver', 'CO', '80202', 'scrypt:32768:8:1$ojcorXVfGZrGxiuk$26013ff7aa9b95de72d400ca4a38b98b814effd47fbd880459c4ff194ba139ca0e38e5e0f79bb8ba8b2349115e96821eddc48c72e824ce952ca2d5b103e36d7e'),
('Bob', 'Smith', 'bob.smith@email.com', '555-1002', '456 Oak Ave', 'Denver', 'CO', '80203', 'scrypt:32768:8:1$ojcorXVfGZrGxiuk$26013ff7aa9b95de72d400ca4a38b98b814effd47fbd880459c4ff194ba139ca0e38e5e0f79bb8ba8b2349115e96821eddc48c72e824ce952ca2d5b103e36d7e'),
('Carol', 'Williams', 'carol.williams@email.com', '555-1003', '789 Pine Rd', 'Aurora', 'CO', '80012', 'scrypt:32768:8:1$ojcorXVfGZrGxiuk$26013ff7aa9b95de72d400ca4a38b98b814effd47fbd880459c4ff194ba139ca0e38e5e0f79bb8ba8b2349115e96821eddc48c72e824ce952ca2d5b103e36d7e'),
('David', 'Brown', 'david.brown@email.com', '555-1004', '321 Elm St', 'Lakewood', 'CO', '80226', 'scrypt:32768:8:1$ojcorXVfGZrGxiuk$26013ff7aa9b95de72d400ca4a38b98b814effd47fbd880459c4ff194ba139ca0e38e5e0f79bb8ba8b2349115e96821eddc48c72e824ce952ca2d5b103e36d7e'),
('Emma', 'Davis', 'emma.davis@email.com', '555-1005', '654 Maple Dr', 'Littleton', 'CO', '80120', 'scrypt:32768:8:1$ojcorXVfGZrGxiuk$26013ff7aa9b95de72d400ca4a38b98b814effd47fbd880459c4ff194ba139ca0e38e5e0f79bb8ba8b2349115e96821eddc48c72e824ce952ca2d5b103e36d7e');

-- Sample Vehicles
INSERT INTO vehicles (customer_id, vin, make, model, year, color) VALUES
(1, '1HGCM82633A123456', 'Honda', 'Accord', 2018, 'Silver'),
(1, '2HGCM82633A123457', 'Honda', 'CR-V', 2020, 'Blue'),
(2, '1G1ZD5ST0LF123458', 'Chevrolet', 'Malibu', 2019, 'Black'),
(3, '5FNRL6H78LB123459', 'Honda', 'Odyssey', 2021, 'White'),
(4, '1FTFW1ET5EFC12460', 'Ford', 'F-150', 2017, 'Red'),
(5, 'WBAJB1C55EWP12461', 'BMW', '328i', 2016, 'Gray');

-- Sample Mechanics
INSERT INTO mechanics (full_name, email, phone, salary, is_active) VALUES
('John Smith', 'john.smith@mechanicshop.com', '555-0101', 65000, 1),
('Sarah Johnson', 'sarah.johnson@mechanicshop.com', '555-0102', 68000, 1),
('Mike Williams', 'mike.williams@mechanicshop.com', '555-0103', 62000, 1),
('Emily Davis', 'emily.davis@mechanicshop.com', '555-0104', 70000, 1),
('Robert Brown', 'robert.brown@mechanicshop.com', '555-0105', 58000, 1);

-- Sample Services
INSERT INTO services (name, default_labor_minutes, base_price_cents) VALUES
('Oil Change', 30, 3500),
('Tire Rotation', 45, 2500),
('Brake Inspection', 60, 5000),
('Brake Pad Replacement', 120, 15000),
('Engine Diagnostic', 90, 8500),
('Air Filter Replacement', 15, 2000),
('Coolant Flush', 60, 7500),
('Transmission Service', 180, 20000),
('Wheel Alignment', 90, 8000),
('Battery Replacement', 30, 12000);

-- Sample Parts (Inventory)
INSERT INTO parts (part_number, name, description, category, manufacturer, current_cost_cents, quantity_in_stock, reorder_level, supplier) VALUES
('OIL-001', 'Engine Oil 5W-30', 'Synthetic blend engine oil, 5 quarts', 'Fluids', 'Mobil 1', 2500, 50, 10, 'Auto Parts Warehouse'),
('FLT-001', 'Oil Filter', 'Standard oil filter for most vehicles', 'Filters', 'FRAM', 800, 75, 15, 'Auto Parts Warehouse'),
('BRK-001', 'Brake Pad Set - Front', 'Ceramic brake pads, front axle', 'Brakes', 'Wagner', 4500, 25, 5, 'Brake Supply Co'),
('BRK-002', 'Brake Pad Set - Rear', 'Ceramic brake pads, rear axle', 'Brakes', 'Wagner', 4200, 20, 5, 'Brake Supply Co'),
('BRK-003', 'Brake Rotor - Front', 'Premium brake rotor, front', 'Brakes', 'Brembo', 6500, 15, 3, 'Brake Supply Co'),
('BRK-004', 'Brake Rotor - Rear', 'Premium brake rotor, rear', 'Brakes', 'Brembo', 6000, 12, 3, 'Brake Supply Co'),
('FLT-002', 'Air Filter', 'Engine air filter', 'Filters', 'K&N', 1500, 40, 10, 'Auto Parts Warehouse'),
('FLT-003', 'Cabin Air Filter', 'HVAC cabin air filter', 'Filters', 'Bosch', 1200, 35, 10, 'Auto Parts Warehouse'),
('BAT-001', 'Car Battery 12V', '650 CCA battery', 'Electrical', 'Interstate', 12000, 20, 5, 'Battery Depot'),
('TIR-001', 'All-Season Tire 215/60R16', 'Standard all-season tire', 'Tires', 'Michelin', 9500, 30, 8, 'Tire Distributors'),
('CLT-001', 'Coolant/Antifreeze', 'Pre-mixed coolant, 1 gallon', 'Fluids', 'Prestone', 1800, 40, 10, 'Auto Parts Warehouse'),
('TRN-001', 'Transmission Fluid', 'ATF transmission fluid, 1 quart', 'Fluids', 'Valvoline', 900, 60, 15, 'Auto Parts Warehouse');

-- Sample Specializations
INSERT INTO specializations (name, description, category) VALUES
('ASE Master Technician', 'Master level automotive service excellence certification', 'General'),
('Brake Specialist', 'Advanced training in brake systems', 'Brakes'),
('Engine Specialist', 'Advanced training in engine repair and diagnostics', 'Engine'),
('Electrical Systems', 'Advanced training in automotive electrical systems', 'Electrical'),
('Transmission Specialist', 'Advanced training in automatic and manual transmissions', 'Transmission'),
('Hybrid/Electric Vehicle', 'Certified for hybrid and electric vehicle service', 'Alternative Fuel'),
('HVAC Systems', 'Climate control systems specialist', 'Climate Control'),
('Suspension & Steering', 'Suspension and steering systems expert', 'Suspension');

-- Sample Mechanic Specializations (Certifications)
INSERT INTO mechanic_specializations (mechanic_id, specialization_id, certified_date, expiration_date, certification_number, proficiency_level) VALUES
(1, 1, '2020-01-15', '2025-01-15', 'ASE-2020-001', 'Expert'),
(1, 3, '2021-03-20', '2026-03-20', 'ENG-2021-001', 'Expert'),
(2, 2, '2019-06-10', '2024-06-10', 'BRK-2019-001', 'Expert'),
(2, 1, '2021-08-15', '2026-08-15', 'ASE-2021-002', 'Advanced'),
(3, 5, '2020-11-20', '2025-11-20', 'TRN-2020-001', 'Expert'),
(4, 4, '2021-02-10', '2026-02-10', 'ELC-2021-001', 'Advanced'),
(4, 6, '2022-05-15', '2027-05-15', 'HEV-2022-001', 'Expert'),
(5, 8, '2020-09-05', '2025-09-05', 'SUS-2020-001', 'Advanced');

-- Sample Service Packages
INSERT INTO service_packages (name, description, package_discount_percentage, is_active, recommended_mileage_interval) VALUES
('Basic Maintenance Package', 'Oil change, tire rotation, and multi-point inspection', 10.0, 1, 5000),
('Premium Maintenance Package', 'Includes basic package plus air filter and fluid top-off', 15.0, 1, 7500),
('Brake Service Package', 'Complete brake inspection and service', 12.0, 1, 30000),
('Major Service Package', '30k/60k/90k mile major service', 20.0, 1, 30000);

-- Sample Service Package Items
INSERT INTO service_package_items (package_id, service_id, quantity, is_optional, discount_percentage, sequence_order) VALUES
-- Basic Maintenance Package
(1, 1, 1, 0, 0, 1),  -- Oil Change
(1, 2, 1, 0, 0, 2),  -- Tire Rotation

-- Premium Maintenance Package
(2, 1, 1, 0, 0, 1),  -- Oil Change
(2, 2, 1, 0, 0, 2),  -- Tire Rotation
(2, 6, 1, 0, 0, 3),  -- Air Filter Replacement

-- Brake Service Package
(3, 3, 1, 0, 0, 1),  -- Brake Inspection
(3, 4, 1, 1, 5, 2),  -- Brake Pad Replacement (optional with extra discount)

-- Major Service Package
(4, 1, 1, 0, 0, 1),  -- Oil Change
(4, 2, 1, 0, 0, 2),  -- Tire Rotation
(4, 6, 1, 0, 0, 3),  -- Air Filter Replacement
(4, 7, 1, 0, 0, 4),  -- Coolant Flush
(4, 8, 1, 1, 10, 5); -- Transmission Service (optional with extra discount)

-- Sample Service Prerequisites
INSERT INTO service_prerequisites (service_id, prerequisite_service_id, is_required, recommended_gap_hours, reason) VALUES
(4, 3, 1, NULL, 'Brake inspection must be completed before brake pad replacement'),
(8, 5, 0, 24, 'Engine diagnostic recommended before transmission service to rule out engine issues');

-- Sample Service Tickets
INSERT INTO service_tickets (vehicle_id, customer_id, status, opened_at, closed_at, problem_description, odometer_miles, priority) VALUES
(1, 1, 'completed', '2025-10-01 09:00:00', '2025-10-01 11:30:00', 'Regular maintenance - oil change and tire rotation', 45000, 2),
(2, 1, 'in_progress', '2025-10-15 10:00:00', NULL, 'Customer reports squeaking noise when braking', 32000, 3),
(3, 2, 'completed', '2025-10-05 14:00:00', '2025-10-06 16:00:00', 'Check engine light is on - needs diagnostic', 58000, 3),
(4, 3, 'pending', '2025-10-18 08:30:00', NULL, 'Annual inspection and maintenance package', 72000, 2),
(5, 4, 'in_progress', '2025-10-16 11:00:00', NULL, 'Transmission slipping, needs inspection', 95000, 4),
(6, 5, 'completed', '2025-10-10 13:00:00', '2025-10-10 14:30:00', 'Battery replacement - car won\'t start', 48000, 5);

-- Sample Ticket Mechanics (Assignments)
INSERT INTO ticket_mechanics (ticket_id, mechanic_id, role, minutes_worked) VALUES
(1, 1, 'Lead Technician', 90),
(2, 2, 'Lead Technician', 120),
(2, 1, 'Assistant', 45),
(3, 1, 'Lead Technician', 180),
(4, 3, 'Lead Technician', 0),
(5, 3, 'Lead Technician', 60),
(6, 4, 'Lead Technician', 45);

-- Sample Ticket Line Items
INSERT INTO ticket_line_items (ticket_id, service_id, line_type, description, quantity, unit_price_cents) VALUES
(1, 1, 'service', 'Oil Change Service', 1.00, 3500),
(1, 2, 'service', 'Tire Rotation', 1.00, 2500),
(2, 3, 'service', 'Brake Inspection', 1.00, 5000),
(2, 4, 'service', 'Front Brake Pad Replacement', 1.00, 15000),
(3, 5, 'service', 'Engine Diagnostic', 1.00, 8500),
(3, 6, 'service', 'Air Filter Replacement', 1.00, 2000),
(5, 8, 'service', 'Transmission Service', 1.00, 20000),
(6, 10, 'service', 'Battery Replacement', 1.00, 12000);

-- Sample Ticket Parts
INSERT INTO ticket_parts (ticket_id, part_id, quantity_used, unit_cost_cents, markup_percentage, installed_date, warranty_months, installed_by_mechanic_id) VALUES
(1, 1, 1, 2500, 30.00, '2025-10-01 10:00:00', 3, 1),
(1, 2, 1, 800, 30.00, '2025-10-01 10:15:00', 3, 1),
(2, 3, 1, 4500, 35.00, '2025-10-15 11:30:00', 12, 2),
(2, 5, 2, 6500, 35.00, '2025-10-15 12:00:00', 12, 2),
(3, 7, 1, 1500, 30.00, '2025-10-05 15:00:00', 12, 1),
(5, 12, 4, 900, 30.00, '2025-10-16 12:00:00', 6, 3),
(6, 9, 1, 12000, 25.00, '2025-10-10 13:30:00', 36, 4);

SELECT 'Sample data seeded successfully!' AS message;
SELECT CONCAT('Created ', COUNT(*), ' customers') AS customers FROM customers;
SELECT CONCAT('Created ', COUNT(*), ' vehicles') AS vehicles FROM vehicles;
SELECT CONCAT('Created ', COUNT(*), ' mechanics') AS mechanics FROM mechanics;
SELECT CONCAT('Created ', COUNT(*), ' services') AS services FROM services;
SELECT CONCAT('Created ', COUNT(*), ' parts') AS parts FROM parts;
SELECT CONCAT('Created ', COUNT(*), ' service tickets') AS service_tickets FROM service_tickets;
SELECT 'Test account password: password123' AS note;
