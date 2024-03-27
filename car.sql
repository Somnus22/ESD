CREATE DATABASE IF NOT EXISTS `Cars` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Cars`;

-- Create table to store car information
CREATE TABLE Cars (
    `vehicle_id` INT PRIMARY KEY,
    `cartype` VARCHAR(64),
    `brand` VARCHAR(64),
    `model` VARCHAR(64),
    `latitude` DECIMAL(10,7),
    `longitude` DECIMAL(10,7),
    `availability` VARCHAR(8),
    `per_hr_price` DECIMAL(10, 2)
);

-- Insert data into the table
INSERT INTO Cars (vehicle_id, cartype, brand, model, availability, per_hr_price, latitude, longitude) VALUES
('1', 'SUV', 'MERCEDES','EQB SUV', 'Unbooked', 10.10, 1.3525000, 103.9447000),
('2', 'SEDAN', 'MERCEDES','GLA SUV', 'Booked', 8.30,34.0522000, -118.2437000),
('3', 'SUV', 'MITSUBISHI','EVO 9', 'Unbooked', 7.50, 1.0000000, 104.0000000),
('4', 'SEDAN', 'MITSUBISHI','OUTLANDER', 'Unbooked', 6.50, 40.7128000,-74.0060000),
('5', 'SUV', 'MAZDA','CX3', 'Damaged', 7.90, 1.0000000,103.000000),
('6', 'SUV', 'AUDI','A5 HATCHBACK','Booked', 9.60,34.0522000, -118.2437000);
