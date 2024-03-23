CREATE DATABASE IF NOT EXISTS `Cars` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Cars`;


-- Create table to store car information
CREATE TABLE Cars (
    Vehicle_Id INT PRIMARY KEY,
    Type VARCHAR(64) NOT NULL,
    Brand VARCHAR(64) NOT NULL,
    Latitude DECIMAL(10,7),
    Longitude DECIMAL(10,7),
    Availability VARCHAR(8) NOT NULL,
    Per_Hr_Price DECIMAL(10, 2) NOT NULL
);

-- Insert data into the table
INSERT INTO Cars (Vehicle_Id, Type, Brand, Availability, Per_Hr_Price, Latitude, Longitude) VALUES
('1', 'SUV', 'MERCEDES', "Unbooked", 10.10, 1.3525000, 103.9447000),
('3', 'SUV', 'MITSUBISHI', "Unbooked", 7.50, 1.0000000, 104.0000000),
('4', 'SEDAN', 'MITSUBISHI', "Unbooked", 6.50, 34.0522000, -118.2437000);

INSERT INTO Cars (Vehicle_Id, Type, Brand, Availability, Per_Hr_Price) VALUES
('2', 'SEDAN', 'MERCEDES', "Booked", 8.30),
('5', 'SUV', 'MAZDA', "Damaged", 7.90),
('6', 'SUV', 'AUDI', "Booked", 9.60);
