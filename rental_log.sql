CREATE DATABASE IF NOT EXISTS `Rental_Log` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Rental_Log`;

SET time_zone = '+08:00';
DROP TABLE IF EXISTS 'rental_log';

CREATE TABLE IF NOT EXISTS 'rental_log' (
    'Log_ID' INT PRIMARY KEY,
    'Log_Entry_Time' TIMESTAMP NOT NULL CURRENT_TIMESTAMP,
    'Log_Entry_Desc' VARCHAR(255) NOT NULL,
    'Vehicle_ID' INT,  
    'User_ID' INT, 
    `Status` varchar(10) NOT NULL DEFAULT 'NEW',
); 
