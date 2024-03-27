CREATE DATABASE IF NOT EXISTS `Users` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Users`;

create table Users (
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