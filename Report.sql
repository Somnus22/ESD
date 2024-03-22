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
  `Report_id` int(11) NOT NULL AUTO_INCREMENT,
  `User_id` int(11) NOT NULL,
  `Vehicle_Id` int(11) NOT NULL,
  `Report_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `Damage`
--

DROP TABLE IF EXISTS damage;
CREATE TABLE IF NOT EXISTS damage (
  `Report_id` int(11) NOT NULL,
  `Damage_num` int(11) NOT NULL,
  `Damage_desc` varchar(300) NOT NULL,
  PRIMARY KEY (report_id, damage_num),
  FOREIGN KEY (report_id) REFERENCES report(report_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
