CREATE DATABASE IF NOT EXISTS `Rental_Log` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Rental_Log`;

SET time_zone = '+08:00';

CREATE TABLE IF NOT EXISTS `rental_log` (
    `Log_Id` INT(11) PRIMARY KEY AUTO_INCREMENT,
    `Log_Entry_Time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `Log_Entry_Desc` VARCHAR(255) NOT NULL,
    `Vehicle_Id` INT(11) NOT NULL,
    `User_Id` INT(11) NOT NULL,
    `Status` VARCHAR(10) NOT NULL DEFAULT 'CONFIRMED'
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
