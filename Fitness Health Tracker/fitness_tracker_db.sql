-- Create Database
CREATE DATABASE fitness_tracker_db;
USE fitness_tracker_db;

-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    age INT,
    height FLOAT,
    weight FLOAT
);

-- Food Log Table
CREATE TABLE food_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    food_name VARCHAR(100),
    quantity INT DEFAULT 1,
    calories FLOAT,
    log_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Exercise Log Table
CREATE TABLE exercise_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    activity VARCHAR(100),
    duration INT,  -- in minutes
    calories_burned FLOAT,
    distance FLOAT,
    log_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Environment Log Table
CREATE TABLE environment_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    distance_walked FLOAT,
    carbon_saved FLOAT,
    log_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Daily Summary Table
CREATE TABLE daily_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date DATE,
    total_calories_consumed FLOAT,
    total_calories_burned FLOAT,
    total_carbon_saved FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
