-- Create table to store car information
CREATE TABLE Cars (
    Vehicle_ID INT PRIMARY KEY,
    Type VARCHAR(50),
    Brand VARCHAR(50),
    Availability BOOLEAN,
    Status varchar (30,)
    Price DECIMAL(10, 2)
);

-- Insert data into the table
INSERT INTO Cars (CarID, Type, Brand, Availability, Price) VALUES
(1, 'SUV', 'MERCEDES', TRUE, "UNDAMAGED", 20.00),
(2, 'SEDAN', 'MERCEDES', FALSE, "UNDAMAGED", 20.00),
(3, 'SUV', 'MITSUBISHI', TRUE, "UNDAMAGED", 15.10),
(4, 'SEDAN', 'MITSUBISHI', TRUE, "UNDAMAGED", 15.10);
