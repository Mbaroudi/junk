-- phpMyAdmin SQL Dump
-- version 3.1.3.1
-- http://www.phpmyadmin.net
--
-- Хост: localhost
-- Время создания: Апр 28 2009 г., 02:52
-- Версия сервера: 5.1.33
-- Версия PHP: 5.2.9-2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- База данных: `gallery`
--

-- --------------------------------------------------------

--
-- Структура таблицы `albums`
--

DROP TABLE IF EXISTS `albums`;
CREATE TABLE IF NOT EXISTS `albums` (
  `id` int(3) NOT NULL COMMENT 'Album ID',
  `name` varchar(100) NOT NULL COMMENT 'Album name',
  `descr` varchar(1000) NOT NULL COMMENT 'Album description',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Image albums';

-- --------------------------------------------------------

--
-- Структура таблицы `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(3) NOT NULL AUTO_INCREMENT COMMENT 'Category ID',
  `name` varchar(100) CHARACTER SET latin1 NOT NULL COMMENT 'Category name',
  `descr` varchar(1000) CHARACTER SET latin1 NOT NULL COMMENT 'category description',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='Image categories' AUTO_INCREMENT=3 ;

-- --------------------------------------------------------

--
-- Структура таблицы `images`
--

DROP TABLE IF EXISTS `images`;
CREATE TABLE IF NOT EXISTS `images` (
  `id` int(8) NOT NULL AUTO_INCREMENT COMMENT 'Image id',
  `name` varchar(100) DEFAULT NULL COMMENT 'Image name',
  `description` varchar(1000) DEFAULT NULL COMMENT 'Image description',
  `date` date DEFAULT NULL COMMENT 'Capture date',
  `full_name` varchar(100) NOT NULL DEFAULT '' COMMENT 'Full-sized image name',
  `norm_name` varchar(100) NOT NULL DEFAULT '' COMMENT 'Normal-sized image name',
  `small_name` varchar(100) NOT NULL COMMENT 'Small-sized image name',
  `bgcolor` varchar(6) DEFAULT NULL COMMENT 'Background color',
  `uploaddate` date NOT NULL COMMENT 'Upload date',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='Image information' AUTO_INCREMENT=196 ;

-- --------------------------------------------------------

--
-- Структура таблицы `imgalbum`
--

DROP TABLE IF EXISTS `imgalbum`;
CREATE TABLE IF NOT EXISTS `imgalbum` (
  `img_id` int(8) NOT NULL COMMENT 'Image id',
  `alb_id` int(3) NOT NULL COMMENT 'Album id',
  PRIMARY KEY (`img_id`,`alb_id`),
  KEY `alb_id` (`alb_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Link between images & albums';

-- --------------------------------------------------------

--
-- Структура таблицы `imgcategory`
--

DROP TABLE IF EXISTS `imgcategory`;
CREATE TABLE IF NOT EXISTS `imgcategory` (
  `img_id` int(8) NOT NULL COMMENT 'Image id',
  `cat_id` int(3) NOT NULL COMMENT 'Category id',
  PRIMARY KEY (`img_id`,`cat_id`),
  KEY `cat_id` (`cat_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Link between images & categories';
