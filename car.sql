-- Create table to store car information
CREATE TABLE Cars (
    Vehicle_ID INT PRIMARY KEY,
    Type VARCHAR(50),
    Brand VARCHAR(50),
    Availability BOOLEAN,
    Price DECIMAL(10, 2)
);

-- Insert data into the table
INSERT INTO Cars (CarID, Type, Brand, Availability, Price) VALUES
(1, 'SUV', 'MERCEDES', TRUE, 20.00),
(2, 'SEDAN', 'MERCEDES', FALSE, 20.00),
(3, 'SUV', 'MITSUBISHI', TRUE, 15.10),
(4, 'SEDAN', 'MITSUBISHI', TRUE, 15.10);
