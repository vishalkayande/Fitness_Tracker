-- Quick fix for user_summary table error
-- Run this in MySQL to remove problematic triggers

USE fitness_tracker_db;

-- Option 1: Find and drop any triggers that reference user_summary
-- This finds triggers that might be causing the issue
SELECT 
    TRIGGER_NAME,
    'DROP TRIGGER IF EXISTS `' || TRIGGER_NAME || '`;' AS drop_command
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'fitness_tracker_db'
AND (
    EVENT_OBJECT_TABLE = 'food_log' 
    OR ACTION_STATEMENT LIKE '%user_summary%'
);

-- Option 2: Show all triggers to see what's there
SHOW TRIGGERS;

-- Option 3: Drop common trigger names if they exist
-- Uncomment the ones that match your trigger names from above:

-- DROP TRIGGER IF EXISTS update_user_summary;
-- DROP TRIGGER IF EXISTS after_food_insert;
-- DROP TRIGGER IF EXISTS food_log_after_insert;
-- DROP TRIGGER IF EXISTS food_log_ai;
-- DROP TRIGGER IF EXISTS update_summary_on_food_insert;

-- Option 4: If you want to create the user_summary table instead:
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





