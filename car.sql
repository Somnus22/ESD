-- Create table to store car information
CREATE TABLE Cars (
    Vehicle_ID INT PRIMARY KEY,
    Type VARCHAR(64),
    Brand VARCHAR(64),
    Latitude DECIMAL(10,7),
    Longitude DECIMAL(10,7),
    Availability INT,
    Price DECIMAL(10, 2)
);

-- Insert data into the table
INSERT INTO Cars (Vehicle_ID, Type, Brand,  Availability, Price) VALUES
(1, 'SUV', 'MERCEDES', TRUE, 20.00),
(2, 'SEDAN', 'MERCEDES', FALSE, 20.00),
(3, 'SUV', 'MITSUBISHI', TRUE, 15.10),
(4, 'SEDAN', 'MITSUBISHI', TRUE, 15.10);
