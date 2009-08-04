-- phpMyAdmin SQL Dump
-- version 3.2.0.1
-- http://www.phpmyadmin.net
--
-- Хост: localhost
-- Время создания: Авг 03 2009 г., 23:53
-- Версия сервера: 5.1.35
-- Версия PHP: 5.2.8

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- База данных: 'gallery'
--

-- --------------------------------------------------------

--
-- Структура таблицы 'albumcategory'
--

DROP TABLE IF EXISTS albumcategory;
CREATE TABLE IF NOT EXISTS albumcategory (
  alb_id int(8) NOT NULL COMMENT 'Album id',
  cat_id int(3) NOT NULL COMMENT 'Category id',
  PRIMARY KEY (alb_id,cat_id),
  KEY cat_id (cat_id),
  KEY alb_id (alb_id),
  KEY fk_albumcategory_album (alb_id),
  KEY fk_albumcategory_category (cat_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Link between images & categories';

--
-- Дамп данных таблицы 'albumcategory'
--

INSERT INTO albumcategory (alb_id, cat_id) VALUES
(-1, -1);

-- --------------------------------------------------------

--
-- Структура таблицы 'albums'
--

DROP TABLE IF EXISTS albums;
CREATE TABLE IF NOT EXISTS albums (
  id int(3) NOT NULL AUTO_INCREMENT COMMENT 'Album ID',
  `name` varchar(100) NOT NULL COMMENT 'Album name',
  descr varchar(1000) NOT NULL COMMENT 'Album description',
  image_id int(8) NOT NULL COMMENT 'Album icon',
  PRIMARY KEY (id),
  KEY fk_albums_image (image_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Image albums' AUTO_INCREMENT=1 ;

--
-- Дамп данных таблицы 'albums'
--

INSERT INTO albums (id, name, descr, image_id) VALUES
(-1, 'Default album', 'Hidden album', -1);

-- --------------------------------------------------------

--
-- Структура таблицы 'categories'
--

DROP TABLE IF EXISTS categories;
CREATE TABLE IF NOT EXISTS categories (
  id int(3) NOT NULL AUTO_INCREMENT COMMENT 'Category ID',
  `name` varchar(100) NOT NULL COMMENT 'Category name',
  descr varchar(1000) NOT NULL COMMENT 'category description',
  image_id int(8) NOT NULL COMMENT 'Category icon',
  PRIMARY KEY (id),
  KEY fk_categories_image (image_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Image categories' AUTO_INCREMENT=1 ;

--
-- Дамп данных таблицы 'categories'
--
	
	INSERT INTO categories (id, name, descr, image_id) VALUES
	(-1, 'Default category', 'Hidden category', -1);

-- --------------------------------------------------------

--
-- Структура таблицы 'images'
--

DROP TABLE IF EXISTS images;
CREATE TABLE IF NOT EXISTS images (
  id int(8) NOT NULL AUTO_INCREMENT COMMENT 'Image id',
  `name` varchar(100) DEFAULT NULL COMMENT 'Image name',
  descr varchar(1000) DEFAULT NULL COMMENT 'Image description',
  img_date date DEFAULT NULL COMMENT 'Capture date',
  full_src varchar(100) NOT NULL COMMENT 'Full-sized image name',
  norm_src varchar(100) NOT NULL COMMENT 'Normal-sized image name',
  thumb_src varchar(100) NOT NULL COMMENT 'Small-sized image name',
  bgcolor varchar(6) DEFAULT NULL COMMENT 'Background color',
  uploaddate date NOT NULL COMMENT 'Upload date',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Image information' AUTO_INCREMENT=1 ;

--
-- Дамп данных таблицы 'images'
--

INSERT INTO images (id, name, descr, img_date, full_src, norm_src, thumb_src, bgcolor, uploaddate) VALUES
(-1, 'Default image', 'Default image', '2000-01-01', 'css/new.jpg', 'css/new.jpg', 'css/new.jpg', '000000', '2000-01-01');

-- --------------------------------------------------------

--
-- Структура таблицы 'imgalbum'
--

DROP TABLE IF EXISTS imgalbum;
CREATE TABLE IF NOT EXISTS imgalbum (
  img_id int(8) NOT NULL COMMENT 'Image id',
  alb_id int(3) NOT NULL COMMENT 'Album id',
  PRIMARY KEY (img_id,alb_id),
  KEY fk_imgalbum_images (img_id),
  KEY fk_imgalbum_albums (alb_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Link between images & albums';

-- --------------------------------------------------------
--
-- Структура для представления `v_albumcategory`
--

CREATE OR REPLACE VIEW v_albumcategory AS 
select c.id AS cat_id,
	c.name AS cat_name,
	c.descr AS cat_descr,
	a.id AS alb_id,
	a.name AS alb_name,
	a.descr AS alb_descr 
from categories c 
	join albumcategory ac on ac.cat_id = c.id 
	join albums a on a.id = ac.alb_id;

-- --------------------------------------------------------

--
-- Структура для представления `v_imgalbum`
--

CREATE OR REPLACE VIEW v_imgalbum AS 
select a.id AS alb_id,
	a.name AS alb_name,
	a.descr AS alb_descr,
	i.id AS img_id,
	i.name AS img_name,
	i.descr AS img_descr,
	i.img_date AS img_date,
	i.full_src AS img_full_name,
	i.norm_src AS img_norm_name,
	i.thumb_src AS img_thumb_name,
	i.bgcolor AS img_bgcolor,
	i.uploaddate AS img_uploaddate 
from albums a 
	join imgalbum ia on ia.alb_id = a.id 
	join images i on i.id = ia.img_id;
	
	
	
	
--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `albumcategory`
--
ALTER TABLE `albumcategory`
  ADD CONSTRAINT fk_albumcategory_album FOREIGN KEY (alb_id) REFERENCES albums (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT fk_albumcategory_category FOREIGN KEY (cat_id) REFERENCES categories (id) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Ограничения внешнего ключа таблицы `albums`
--
ALTER TABLE `albums`
  ADD CONSTRAINT fk_albums_image FOREIGN KEY (image_id) REFERENCES images (id) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Ограничения внешнего ключа таблицы `categories`
--
ALTER TABLE `categories`
  ADD CONSTRAINT fk_categories_image FOREIGN KEY (image_id) REFERENCES images (id) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Ограничения внешнего ключа таблицы `imgalbum`
--
ALTER TABLE `imgalbum`
  ADD CONSTRAINT fk_imgalbum_albums FOREIGN KEY (alb_id) REFERENCES albums (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT fk_imgalbum_images FOREIGN KEY (img_id) REFERENCES images (id) ON DELETE NO ACTION ON UPDATE NO ACTION;


