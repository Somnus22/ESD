CREATE TABLE rental_log (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    LogEntryTime DATETIME NOT NULL,
    LogEntryDesc VARCHAR(255) NOT NULL,
    CarID INT,  -- Foreign key reference to Car table
    UserID INT,  -- Foreign key reference to Users table
    FOREIGN KEY (CarID) REFERENCES car(CarID),
    FOREIGN KEY (UserID) REFERENCES users(userID)
);
