-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = '+08:00';

-- Database: `Report`
--
CREATE DATABASE IF NOT EXISTS `report` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `report`;

-- --------------------------------------------------------

--
-- Table structure for table `Report`
--

DROP TABLE IF EXISTS `report`;
CREATE TABLE IF NOT EXISTS `report` (
  `report_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `car_id` int(11) NOT NULL,
  `report_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `Damage`
--

DROP TABLE IF EXISTS damage;
CREATE TABLE IF NOT EXISTS damage (
  report_id int(11) NOT NULL,
  damage_num int(11) NOT NULL,
  damage_desc varchar(300) NOT NULL,
  PRIMARY KEY (report_id, damage_num),
  FOREIGN KEY (report_id) REFERENCES report(report_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
