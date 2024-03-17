SET time_zone = '+08:00';
DROP TABLE IF EXISTS 'rental log';

CREATE TABLE IF NOT EXISTS 'rental_log' (
    'LogID' INT PRIMARY KEY,
    'LogEntryTime' TIMESTAMP NOT NULL CURRENT_TIMESTAMP,
    'LogEntryDesc' VARCHAR(255) NOT NULL,
    'CarID' INT,  
    'UserID' INT, 
    FOREIGN KEY (CarID) REFERENCES car(CarID),
    FOREIGN KEY (UserID) REFERENCES users(userID)
); 
