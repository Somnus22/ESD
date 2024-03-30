-- ----------USERS----------------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS `Users` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Users`;

DROP TABLE IF EXISTS `Users`;
CREATE TABLE IF NOT EXISTS `Users` (
	`user_id` INT PRIMARY KEY AUTO_INCREMENT,
	`name` VARCHAR(50),
	`phone_number` VARCHAR(50),
	`email_address` VARCHAR(50)
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

INSERT INTO Users (user_id, name, phone_number, email_address) VALUES
(1, 'Brad Goh', '+65 9123 4567', 'changethewoah@example.com'),
(2, 'Elliot Tan', '+65 9876 5432', 'Elliot@example.com'),
(3, 'Teo Yong Ray', '+65 8765 4321', 'YongRay@example.com'),
(4, 'William Tan', '+65 7654 3210', 'Weel@example.com'),
(5, 'Jerome Lee', '+65 6543 2109', 'JeromeLee@example.com'),
(6, 'Dominic Jovin', '+65 5432 1098', 'Dom@example.com'),
(7, 'David Afvilla Kumar', '+65 4321 0987', 'Davidee@example.com'),
(8, 'S. Iswaran', '+65 3210 9876', 'getcharged@example.com'),
(9, 'Lily Kong', '+65 2109 8765', 'smuboss@example.com'),
(10, 'Goh Wei Jie', '+65 1098 7654', 'gohweijie@example.com');
-- ----------USERS----------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------------------
-- ----------CARS-----------------------------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS `Cars` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Cars`;

-- Create table to store car information
DROP TABLE IF EXISTS `Cars`;
CREATE TABLE IF NOT EXISTS Cars (
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
('2', 'SEDAN', 'MERCEDES','GLA SUV', 'Booked', 8.30, 1.31056, 103.86420),
('3', 'SUV', 'MITSUBISHI','EVO 9', 'Unbooked', 7.50, 1.35104, 103.87140),
('4', 'SEDAN', 'MITSUBISHI','OUTLANDER', 'Unbooked', 6.50, 1.31801, 103.89140),
('5', 'SUV', 'MAZDA','CX3', 'Damaged', 7.90, 1.34690, 103.70966),
('6', 'SUV', 'AUDI','A5 HATCHBACK','Booked', 9.60, 1.44845, 103.81928);
-- ----------CARS------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------------------
-- ----------REPORTS---------------------------------------------------------------------------------
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = '+08:00';

CREATE DATABASE IF NOT EXISTS `Report` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Report`;

DROP TABLE IF EXISTS `Damage`;
DROP TABLE IF EXISTS `Report`;

CREATE TABLE IF NOT EXISTS `Report` (
  `report_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `vehicle_id` int(11) NOT NULL,
  `report_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Damage` (
  `report_id` int(11) NOT NULL,
  `damage_num` int(11) NOT NULL,
  `damage_desc` varchar(300) NOT NULL,
  PRIMARY KEY (report_id, damage_num),
  FOREIGN KEY (report_id) REFERENCES report(report_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------REPORTS---------------------------------------------------------------------------------
-- --------------------------------------------------------------------------------------------------
-- ----------RENTAL LOG------------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS `Rental_Log` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Rental_Log`;

SET time_zone = '+08:00';

DROP TABLE IF EXISTS `Rental_Log`;
CREATE TABLE IF NOT EXISTS `Rental_Log` (
    `log_id` INT(11) PRIMARY KEY AUTO_INCREMENT,
    `log_entry_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `vehicle_id` INT(11) NOT NULL,
    `user_id` INT(11) NOT NULL,
    `status` VARCHAR(10) NOT NULL DEFAULT 'CONFIRMED'
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
-- --------------------------------------------------------------------------------------------------
-- ----------RENTAL LOG------------------------------------------------------------------------------