-- Create the Users database if it doesn't exist
CREATE DATABASE IF NOT EXISTS `Users` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

-- Switch to the Users database
USE `Users`;

-- Create table to store user information
CREATE TABLE IF NOT EXISTS users (
    userID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(30) NOT NULL,
    phoneNumber VARCHAR(20) NOT NULL,
    emailAddress VARCHAR(64) NOT NULL
);

-- Insert data into the Users table
INSERT INTO users (name, phoneNumber, emailAddress) VALUES
('Dominic Jovin','+0123456789','dominicjovin7@gmail.com'),
('John Doe', '+1234567890', 'john.doe@example.com'),
('Jane Smith', '+1987654321', 'jane.smith@example.com'),
('Michael Johnson', '+1122334455', 'michael.johnson@example.com');
