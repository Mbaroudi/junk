-- База данных: `gallery`
-- --------------------------------------------------------

--
-- Структура таблицы `albumcategory`
--

CREATE TABLE IF NOT EXISTS "albumcategory" (
  "alb_id" int(8) NOT NULL COMMENT 'Album id',
  "cat_id" int(3) NOT NULL COMMENT 'Category id',
  PRIMARY KEY ("alb_id","cat_id"),
  KEY "cat_id" ("cat_id")
);

--
-- Дамп данных таблицы `albumcategory`
--

INSERT INTO `albumcategory` (`alb_id`, `cat_id`) VALUES
(0, 0);

-- --------------------------------------------------------

--
-- Структура таблицы `albums`
--

CREATE TABLE IF NOT EXISTS "albums" (
  "id" int(3) NOT NULL COMMENT 'Album ID',
  "name" varchar(100) NOT NULL COMMENT 'Album name',
  "descr" varchar(1000) NOT NULL COMMENT 'Album description',
  PRIMARY KEY ("id")
);

--
-- Дамп данных таблицы `albums`
--

INSERT INTO `albums` (`id`, `name`, `descr`) VALUES
(0, 'Album #1', 'Album #1 description');

-- --------------------------------------------------------

--
-- Структура таблицы `categories`
--

CREATE TABLE IF NOT EXISTS "categories" (
  "id" int(3) NOT NULL AUTO_INCREMENT COMMENT 'Category ID',
  "name" varchar(100) CHARACTER SET latin1 NOT NULL COMMENT 'Category name',
  "descr" varchar(1000) CHARACTER SET latin1 NOT NULL COMMENT 'category description',
  PRIMARY KEY ("id"),
  UNIQUE KEY "name" ("name")
) AUTO_INCREMENT=4 ;

--
-- Дамп данных таблицы `categories`
--

INSERT INTO `categories` (`id`, `name`, `descr`) VALUES
(0, 'Category #1', 'Category description #1');

-- --------------------------------------------------------

--
-- Структура таблицы `images`
--

CREATE TABLE IF NOT EXISTS "images" (
  "id" int(8) NOT NULL AUTO_INCREMENT COMMENT 'Image id',
  "name" varchar(100) DEFAULT NULL COMMENT 'Image name',
  "descr" varchar(1000) DEFAULT NULL COMMENT 'Image description',
  "img_date" date DEFAULT NULL COMMENT 'Capture date',
  "full_src" varchar(100) NOT NULL COMMENT 'Full-sized image name',
  "norm_src" varchar(100) NOT NULL COMMENT 'Normal-sized image name',
  "small_src" varchar(100) NOT NULL COMMENT 'Small-sized image name',
  "bgcolor" varchar(6) DEFAULT NULL COMMENT 'Background color',
  "uploaddate" date NOT NULL COMMENT 'Upload date',
  PRIMARY KEY ("id")
) AUTO_INCREMENT=198 ;

--
-- Дамп данных таблицы `images`
--

INSERT INTO `images` (`id`, `name`, `descr`, `img_date`, `full_src`, `norm_src`, `small_src`, `bgcolor`, `uploaddate`) VALUES
(0, 'Image #1', 'Image #1 description', '2009-07-06', 'img/full/00.jpg', 'img/norm/00.jpg', 'img/small/00.jpg', '#00000', '2009-07-05');

-- --------------------------------------------------------

--
-- Структура таблицы `imgalbum`
--

CREATE TABLE IF NOT EXISTS "imgalbum" (
  "img_id" int(8) NOT NULL COMMENT 'Image id',
  "alb_id" int(3) NOT NULL COMMENT 'Album id',
  PRIMARY KEY ("img_id","alb_id"),
  KEY "alb_id" ("alb_id")
);

--
-- Дамп данных таблицы `imgalbum`
--

INSERT INTO `imgalbum` (`img_id`, `alb_id`) VALUES
(0, 0);

-- --------------------------------------------------------

--
-- Структура для представления `v_albumcategory`
--

CREATE OR REPLACE VIEW "gallery"."v_albumcategory" AS select "c"."id" AS "cat_id","c"."name" AS "cat_name","c"."descr" AS "cat_descr","a"."id" AS "alb_id","a"."name" AS "alb_name","a"."descr" AS "alb_descr" from (("gallery"."categories" "c" join "gallery"."albumcategory" "ac" on(("ac"."cat_id" = "c"."id"))) join "gallery"."albums" "a" on(("a"."id" = "ac"."alb_id")));

-- --------------------------------------------------------

--
-- Структура для представления `v_imgalbum`
--

CREATE OR REPLACE VIEW "gallery"."v_imgalbum" AS select "a"."id" AS "alb_id","a"."name" AS "alb_name","a"."descr" AS "alb_descr","i"."id" AS "img_id","i"."name" AS "img_name","i"."descr" AS "img_descr","i"."img_date" AS "img_date","i"."full_src" AS "img_full_name","i"."norm_src" AS "img_norm_name","i"."small_src" AS "img_small_name","i"."bgcolor" AS "img_bgcolor","i"."uploaddate" AS "img_uploaddate" from (("gallery"."albums" "a" join "gallery"."imgalbum" "ia" on(("ia"."alb_id" = "a"."id"))) join "gallery"."images" "i" on(("i"."id" = "ia"."img_id")));

