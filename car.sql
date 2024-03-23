CREATE DATABASE IF NOT EXISTS `Cars` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Cars`;


-- Create table to store car information
CREATE TABLE Cars (
    Vehicle_Id INT PRIMARY KEY,
    Type VARCHAR(64),
    Brand VARCHAR(64),
    Model VARCHAR(64),
    Latitude DECIMAL(10,7),
    Longitude DECIMAL(10,7),
    Availability VARCHAR(8),
    Per_Hr_Price DECIMAL(10, 2)
);

-- Insert data into the table
INSERT INTO Cars (Vehicle_Id, Type, Brand, Model, Availability, Per_Hr_Price, Latitude, Longitude) VALUES
('1', 'SUV', 'MERCEDES','EQB SUV', 'Unbooked', 10.10, 1.3525000, 103.9447000),
('2', 'SEDAN', 'MERCEDES','GLA SUV', 'Booked', 8.30),
('3', 'SUV', 'MITSUBISHI','EVO 9', 'Unbooked', 7.50, 1.0000000, 104.0000000);
('4', 'SEDAN', 'MITSUBISHI','OUTLANDER', 'Unbooked', 6.50, 34.0522000, -118.2437000),
('5', 'SUV', 'MAZDA','CX3' 'Damaged', 7.90),
('6', 'SUV', 'AUDI','A5 HATCHBACK','Booked', 9.60);

