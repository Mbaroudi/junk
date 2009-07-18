-- phpMyAdmin SQL Dump
-- version 3.2.0.1
-- http://www.phpmyadmin.net
--
-- Хост: localhost
-- Время создания: Июл 18 2009 г., 19:08
-- Версия сервера: 5.1.35
-- Версия PHP: 5.2.8

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

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
  KEY cat_id (cat_id)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Link between images & categories';

--
-- Дамп данных таблицы 'albumcategory'
--

INSERT INTO albumcategory (alb_id, cat_id) VALUES
(0, 0),
(1, 0),
(2, 1);

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
  PRIMARY KEY (id)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Image albums' AUTO_INCREMENT=3;

--
-- Дамп данных таблицы 'albums'
--

INSERT INTO albums (id, name, descr, image_id) VALUES
(0, 'Album #1', 'Album #1 description', 0),
(1, 'Album #2', 'Album #2 descr', 1),
(2, 'Album #3', 'Album #3 descr', 2);

-- --------------------------------------------------------

--
-- Структура таблицы 'categories'
--

DROP TABLE IF EXISTS categories;
CREATE TABLE IF NOT EXISTS categories (
  id int(3) NOT NULL AUTO_INCREMENT COMMENT 'Category ID',
  `name` varchar(100) CHARACTER SET latin1 NOT NULL COMMENT 'Category name',
  descr varchar(1000) CHARACTER SET latin1 NOT NULL COMMENT 'category description',
  image_id int(8) NOT NULL COMMENT 'Category icon',
  PRIMARY KEY (id),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='Image categories' AUTO_INCREMENT=2;

--
-- Дамп данных таблицы 'categories'
--

INSERT INTO categories (id, name, descr, image_id) VALUES
(0, 'Category #1', 'Category description #1', 0),
(1, 'Category #2', 'Category #2 description', 4);

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
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='Image information' AUTO_INCREMENT=25;

--
-- Дамп данных таблицы 'images'
--

INSERT INTO images (id, name, descr, img_date, full_src, norm_src, thumb_src, bgcolor, uploaddate) VALUES
(0, '0', NULL, NULL, 'img/full/07.jpg', 'img/norm/07.jpg', 'img/thumb/07.jpg', NULL, '2009-07-18'),
(1, '1', NULL, NULL, 'img/full/08.jpg', 'img/norm/08.jpg', 'img/thumb/08.jpg', NULL, '2009-07-18'),
(2, '1', NULL, NULL, 'img/full/12.jpg', 'img/norm/12.jpg', 'img/thumb/12.jpg', NULL, '2009-07-18'),
(3, '1', NULL, NULL, 'img/full/22.jpg', 'img/norm/22.jpg', 'img/thumb/22.jpg', NULL, '2009-07-18'),
(4, '1', NULL, NULL, 'img/full/15.jpg', 'img/norm/15.jpg', 'img/thumb/15.jpg', NULL, '2009-07-18'),
(24, '1', NULL, NULL, 'img/full/01.jpg', 'img/norm/01.jpg', 'img/thumb/01.jpg', NULL, '2009-07-18'),
(23, '1', NULL, NULL, 'img/full/25.jpg', 'img/norm/25.jpg', 'img/thumb/25.jpg', NULL, '2009-07-18'),
(22, '1', NULL, NULL, 'img/full/03.jpg', 'img/norm/03.jpg', 'img/thumb/03.jpg', NULL, '2009-07-18'),
(21, '1', NULL, NULL, 'img/full/04.jpg', 'img/norm/04.jpg', 'img/thumb/04.jpg', NULL, '2009-07-18'),
(20, '1', NULL, NULL, 'img/full/24.jpg', 'img/norm/24.jpg', 'img/thumb/24.jpg', NULL, '2009-07-18'),
(19, '1', NULL, NULL, 'img/full/16.jpg', 'img/norm/16.jpg', 'img/thumb/16.jpg', NULL, '2009-07-18'),
(18, '1', NULL, NULL, 'img/full/09.jpg', 'img/norm/09.jpg', 'img/thumb/09.jpg', NULL, '2009-07-18'),
(17, '1', NULL, NULL, 'img/full/23.jpg', 'img/norm/23.jpg', 'img/thumb/23.jpg', NULL, '2009-07-18'),
(16, '1', NULL, NULL, 'img/full/06.jpg', 'img/norm/06.jpg', 'img/thumb/06.jpg', NULL, '2009-07-18'),
(15, '1', NULL, NULL, 'img/full/18.jpg', 'img/norm/18.jpg', 'img/thumb/18.jpg', NULL, '2009-07-18'),
(14, '1', NULL, NULL, 'img/full/14.jpg', 'img/norm/14.jpg', 'img/thumb/14.jpg', NULL, '2009-07-18'),
(13, '1', NULL, NULL, 'img/full/20.jpg', 'img/norm/20.jpg', 'img/thumb/20.jpg', NULL, '2009-07-18'),
(12, '1', NULL, NULL, 'img/full/13.jpg', 'img/norm/13.jpg', 'img/thumb/13.jpg', NULL, '2009-07-18'),
(11, '1', NULL, NULL, 'img/full/17.jpg', 'img/norm/17.jpg', 'img/thumb/17.jpg', NULL, '2009-07-18'),
(10, '1', NULL, NULL, 'img/full/21.jpg', 'img/norm/21.jpg', 'img/thumb/21.jpg', NULL, '2009-07-18'),
(9, '1', NULL, NULL, 'img/full/19.jpg', 'img/norm/19.jpg', 'img/thumb/19.jpg', NULL, '2009-07-18'),
(8, '1', NULL, NULL, 'img/full/10.jpg', 'img/norm/10.jpg', 'img/thumb/10.jpg', NULL, '2009-07-18'),
(7, '1', NULL, NULL, 'img/full/02.jpg', 'img/norm/02.jpg', 'img/thumb/02.jpg', NULL, '2009-07-18'),
(6, '1', NULL, NULL, 'img/full/05.jpg', 'img/norm/05.jpg', 'img/thumb/05.jpg', NULL, '2009-07-18'),
(5, '1', NULL, NULL, 'img/full/11.jpg', 'img/norm/11.jpg', 'img/thumb/11.jpg', NULL, '2009-07-18');

-- --------------------------------------------------------

--
-- Структура таблицы 'imgalbum'
--

DROP TABLE IF EXISTS imgalbum;
CREATE TABLE IF NOT EXISTS imgalbum (
  img_id int(8) NOT NULL COMMENT 'Image id',
  alb_id int(3) NOT NULL COMMENT 'Album id',
  PRIMARY KEY (img_id,alb_id),
  KEY alb_id (alb_id)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Link between images & albums';

--
-- Дамп данных таблицы 'imgalbum'
--

INSERT INTO imgalbum (img_id, alb_id) VALUES
(0, 0),
(1, 1),
(2, 0),
(3, 0),
(4, 0),
(5, 2),
(6, 1),
(7, 2),
(8, 1),
(9, 1),
(10, 0),
(11, 2),
(12, 0),
(13, 2),
(14, 1),
(15, 0),
(16, 1),
(17, 2),
(18, 2),
(19, 1),
(20, 0),
(21, 1),
(22, 0),
(23, 0),
(24, 0);

-- --------------------------------------------------------

--
-- Дублирующая структура для представления 'v_albumcategory'
--
DROP VIEW IF EXISTS `v_albumcategory`;
CREATE TABLE IF NOT EXISTS `v_albumcategory` (
`cat_id` int(3)
,`cat_name` varchar(100)
,`cat_descr` varchar(1000)
,`alb_id` int(3)
,`alb_name` varchar(100)
,`alb_descr` varchar(1000)
);
-- --------------------------------------------------------

--
-- Дублирующая структура для представления 'v_imgalbum'
--
DROP VIEW IF EXISTS `v_imgalbum`;
CREATE TABLE IF NOT EXISTS `v_imgalbum` (
`alb_id` int(3)
,`alb_name` varchar(100)
,`alb_descr` varchar(1000)
,`img_id` int(8)
,`img_name` varchar(100)
,`img_descr` varchar(1000)
,`img_date` date
,`img_full_name` varchar(100)
,`img_norm_name` varchar(100)
,`img_thumb_name` varchar(100)
,`img_bgcolor` varchar(6)
,`img_uploaddate` date
);
-- --------------------------------------------------------

--
-- Структура для представления 'v_albumcategory'
--
--DROP TABLE IF EXISTS `v_albumcategory`;

--CREATE ALGORITHM=UNDEFINED DEFINER=gallery@`%` SQL SECURITY DEFINER VIEW gallery.v_albumcategory AS select c.id AS cat_id,c.`name` AS cat_name,c.descr AS cat_descr,a.id AS alb_id,a.`name` AS alb_name,a.descr AS alb_descr from ((gallery.categories c join gallery.albumcategory ac on((ac.cat_id = c.id))) join gallery.albums a on((a.id = ac.alb_id)));

-- --------------------------------------------------------

--
-- Структура для представления 'v_imgalbum'
--
--DROP TABLE IF EXISTS `v_imgalbum`;

--CREATE ALGORITHM=UNDEFINED DEFINER=gallery@`%` SQL SECURITY DEFINER VIEW gallery.v_imgalbum AS select a.id AS alb_id,a.`name` AS alb_name,a.descr AS alb_descr,i.id AS img_id,i.`name` AS img_name,i.descr AS img_descr,i.img_date AS img_date,i.full_src AS img_full_name,i.norm_src AS img_norm_name,i.thumb_src AS img_thumb_name,i.bgcolor AS img_bgcolor,i.uploaddate AS img_uploaddate from ((gallery.albums a join gallery.imgalbum ia on((ia.alb_id = a.id))) join gallery.images i on((i.id = ia.img_id)));

-----------------------------------------------------------
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

