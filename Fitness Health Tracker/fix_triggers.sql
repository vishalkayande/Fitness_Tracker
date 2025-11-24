-- SQL script to check and remove triggers that reference user_summary table
-- Run this in your MySQL database to fix the issue

USE fitness_tracker_db;

-- Step 1: Check all triggers in the database
SHOW TRIGGERS;

-- Step 2: Find triggers that might reference user_summary table
SELECT 
    TRIGGER_NAME, 
    EVENT_MANIPULATION, 
    EVENT_OBJECT_TABLE, 
    ACTION_STATEMENT,
    ACTION_TIMING
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'fitness_tracker_db'
AND (
    EVENT_OBJECT_TABLE = 'food_log' 
    OR ACTION_STATEMENT LIKE '%user_summary%'
);

-- Step 3: If you find any triggers referencing user_summary, drop them
-- Replace 'trigger_name_here' with the actual trigger name from Step 2
-- Common trigger names might be: update_user_summary, after_food_insert, etc.

-- Example: Drop trigger if it exists
-- DROP TRIGGER IF EXISTS update_user_summary;
-- DROP TRIGGER IF EXISTS after_food_insert;
-- DROP TRIGGER IF EXISTS food_log_after_insert;

-- Step 4: Alternative solution - Create the user_summary table if it was intended
-- Uncomment the following if you want to create the user_summary table instead:

/*
CREATE TABLE IF NOT EXISTS user_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    total_calories_consumed FLOAT DEFAULT 0,
    total_calories_burned FLOAT DEFAULT 0,
    total_carbon_saved FLOAT DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
*/

-- Step 5: If you want to add a unique constraint to daily_summary for ON DUPLICATE KEY UPDATE:
-- ALTER TABLE daily_summary ADD UNIQUE KEY unique_user_date (user_id, date);

-- After running this script, the food log insertion should work without errors.

