-- ------------------------------------------------------------
-- SQL Evidence: Digital Ledger for Patrol Post Logs
-- Database: securecheck_db
-- ------------------------------------------------------------

-- 1. Verify database and tables
SHOW DATABASES;
USE securecheck_db;
SHOW TABLES;

-- 2. Describe the structure of main table
DESCRIBE traffic_stops;

-- 3. Record count check
SELECT COUNT(*) AS total_records FROM traffic_stops;

-- 4. Display a few recent entries
SELECT * FROM traffic_stops ORDER BY id DESC LIMIT 10;

-- 5. Count records by country
SELECT country_name, COUNT(*) AS total_stops
FROM traffic_stops
GROUP BY country_name
ORDER BY total_stops DESC;

-- 6. Arrests by gender
SELECT driver_gender, SUM(is_arrested) AS total_arrests
FROM traffic_stops
GROUP BY driver_gender;

-- 7. Most common violations
SELECT violation, COUNT(*) AS total
FROM traffic_stops
GROUP BY violation
ORDER BY total DESC
LIMIT 5;

-- 8. Search rate by country
SELECT country_name,
       ROUND(AVG(search_conducted)*100,2) AS search_rate_percent
FROM traffic_stops
GROUP BY country_name
ORDER BY search_rate_percent DESC;

-- 9. Average driver age per violation type
SELECT violation,
       ROUND(AVG(driver_age),1) AS avg_age
FROM traffic_stops
GROUP BY violation;

-- 10. Violation pattern by race and gender
SELECT driver_race, driver_gender, violation, COUNT(*) AS total
FROM traffic_stops
GROUP BY driver_race, driver_gender, violation
ORDER BY total DESC
LIMIT 10;

-- 11. Hourly stop trend
SELECT stop_hour, COUNT(*) AS total
FROM traffic_stops
GROUP BY stop_hour
ORDER BY stop_hour;

-- 12. Arrest ratio per country
SELECT country_name,
       SUM(is_arrested) AS total_arrests,
       COUNT(*) AS total_stops,
       ROUND(SUM(is_arrested)/COUNT(*)*100,2) AS arrest_rate_percent
FROM traffic_stops
GROUP BY country_name
ORDER BY arrest_rate_percent DESC;

-- 13. Drug-related stops summary
SELECT country_name, SUM(drugs_related_stop) AS drug_cases
FROM traffic_stops
GROUP BY country_name
ORDER BY drug_cases DESC;

-- 14. Search vs Arrest correlation
SELECT search_conducted,
       AVG(is_arrested)*100 AS arrest_percentage
FROM traffic_stops
GROUP BY search_conducted;

-- 15. Total distinct vehicle records
SELECT COUNT(DISTINCT vehicle_number) AS distinct_vehicles
FROM traffic_stops;
