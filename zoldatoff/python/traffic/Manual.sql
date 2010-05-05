# Create additional tables

CREATE TABLE jams2 AS 
SELECT edge_group, jam_time, jam_speed, 
	  dayofyear(jam_time)-10 d, HOUR(jam_time) h, MINUTE(jam_time) m
FROM jams
 
drop table jams3

CREATE TABLE `jams3` (
  `edge_group` int(11) NOT NULL,
  `jam_time` datetime NOT NULL,
  `jam_speed` int(11) NOT NULL,
  `d` int(4) DEFAULT NULL,
  `h` int(2) DEFAULT NULL,
  `m` int(2) DEFAULT NULL,
  `t` bigint(17) NOT NULL DEFAULT '0',
  PRIMARY KEY (`edge_group`,`t`),
  KEY `edge_group_idx` (`edge_group`)
) as
SELECT edge_group, jam_time, jam_speed, d, h, m, d*24*60+h*60+m t
FROM jams2

#SELECT jam_time, jam_time + INTERVAL 2 MINUTE FROM result LIMIT 30

CREATE TABLE result2 AS 
SELECT edge_group, jam_time, 
	  dayofyear(jam_time)-10 d, HOUR(jam_time) h, MINUTE(jam_time) m
FROM result

CREATE TABLE `result3` (
  `edge_group` INT(11) NOT NULL,
  `jam_time` DATETIME NOT NULL,
  `d` INT(4) DEFAULT NULL,
  `h` INT(2) DEFAULT NULL,
  `m` INT(2) DEFAULT NULL,
  `t` BIGINT(17) NOT NULL DEFAULT '0',
  PRIMARY KEY (`edge_group`,`t`),
  KEY `edge_group_idx` (`edge_group`)
) AS
SELECT edge_group, jam_time, d, h, m, d*24*60+h*60+m t
FROM result2

##############
# Устанавливаем стандартные времена 17:50 17:54 17:58 18:02 18:04 и т.д.

CREATE TABLE jams0 (
  `edge_group` INT(11) NOT NULL,
  `jam_time` DATETIME NOT NULL,
  `jam_speed` INT(11) NOT NULL,
  `d` INT(4) DEFAULT NULL,
  `h` INT(2) DEFAULT NULL,
  `m` INT(2) DEFAULT NULL,
  `t` BIGINT(17) NOT NULL DEFAULT '0',
  PRIMARY KEY (`edge_group`,`t`),
  KEY `edge_group_idx` (`edge_group`),
  KEY `edge_day` (`edge_group`,`d`)
) AS
SELECT edge_group, jam_time, jam_speed,
		dayofyear(jam_time)-10 d, 
		HOUR(jam_time) h, 
		MINUTE(jam_time) m,
		t
FROM
(
	SELECT edge_group, 
			CASE WHEN t%4 = 2 THEN jam_time ELSE jam_time + INTERVAL 2 MINUTE END AS jam_time,
			jam_speed,
			CASE WHEN t%4 = 2 THEN t ELSE t+2 END AS t
	FROM jams3
) j3

CREATE TABLE result0 (
  `edge_group` INT(11) NOT NULL,
  `jam_time` DATETIME NOT NULL,
  `d` INT(4) DEFAULT NULL,
  `h` INT(2) DEFAULT NULL,
  `m` INT(2) DEFAULT NULL,
  `t` BIGINT(17) NOT NULL DEFAULT '0',
  PRIMARY KEY (`edge_group`,`t`),
  KEY `edge_group_idx` (`edge_group`)
) AS
SELECT edge_group, jam_time,
		dayofyear(jam_time)-10 d, 
		HOUR(jam_time) h, 
		MINUTE(jam_time) m,
		t
FROM
(
	SELECT edge_group, 
			CASE WHEN t%4 = 2 THEN jam_time ELSE jam_time - INTERVAL 2 MINUTE END AS jam_time,
			CASE WHEN t%4 = 2 THEN t ELSE t-2 END AS t
	FROM result3
) r3

#####################

CREATE TABLE hm AS
SELECT DISTINCT h, m FROM jams0 ORDER BY h, m

create table edge_avg_speed as
select edge_group, round(avg(jam_speed),0) jam_speed from jams0 where h >= 18 group by edge_group

##########################################
# Manual calculations

CREATE TABLE task (
  `edge_group` int(11) NOT NULL,
  `t` bigint(17) NOT NULL DEFAULT '0',
  `jam_speed` int(3) not null default '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8

# Выгрузка результата
select r.edge_group, 
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime, 
   	   case when ifnull(t.jam_speed,0) <= 0 then ifnull(j.jam_speed, 50) else t.jam_speed end speed
from result0 r 
	 left join task t on r.t = t.t and r.edge_group = t.edge_group
	 left join edge_avg_speed j on j.edge_group = r.edge_group
into outfile '/tmp/20100502.txt';

# Экспериментальная выгрузка результата
select r.edge_group, 
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime, 
   	   case when ifnull(j.jam_speed, ifnull(t.jam_speed, 50)) <= 0 then 50 else ifnull(j.jam_speed, ifnull(t.jam_speed, 50)) end speed
from result0 r 
	 left join task t on r.t = t.t and r.edge_group = t.edge_group
	 left join edge_avg_speed j on j.edge_group = r.edge_group
into outfile '/tmp/20100502.txt';

scp zoldatoff@pro.local:/tmp/20100428.txt ~/Downloads
scp pro:/tmp/20*.txt ~/Downloads

# Оценка результата 
# http://imat2010.yandex.ru/datasets
select sum(e.length/120 * (1+(t.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed))/count(*)
from task t
	inner join jams0 j on t.edge_group = j.edge_group and t.t = j.t
	inner join edge_data e on e.edge_group = t.edge_group
	
# Анализ результата
select t.edge_group, sum(abs(t.jam_speed - j.jam_speed))/count(*)
from task t
	inner join jams0 j on t.edge_group = j.edge_group and t.t = j.t
	inner join edge_data e on e.edge_group = t.edge_group
group by t.edge_group
order by 2 desc
limit 2000

# Подробный анализ
select j0.t,
	  t.jam_speed,
	  j1.jam_speed,
	  j2.jam_speed,
	  j3.jam_speed,
	  j4.jam_speed,
	  j5.jam_speed,
	  j6.jam_speed
from (select edge_group, h, m, t from jams0 where edge_group = 458880 and d=30) j0
    left join task_t01 t on t.t = j0.t and t.edge_group = j0.edge_group
	left join jams0 j1 on j1.edge_group = j0.edge_group and j1.h = j0.h and j1.m = j0.m and j1.d = 30
	left join jams0 j2 on j2.edge_group = j0.edge_group and j2.h = j0.h and j2.m = j0.m and j2.d = 17
	left join jams0 j3 on j3.edge_group = j0.edge_group and j3.h = j0.h and j3.m = j0.m and j3.d = 2
	left join jams0 j4 on j4.edge_group = j0.edge_group and j4.h = j0.h and j4.m = j0.m and j4.d = 3
	left join jams0 j5 on j5.edge_group = j0.edge_group and j5.h = j0.h and j5.m = j0.m and j5.d = 4
	left join jams0 j6 on j6.edge_group = j0.edge_group and j6.h = j0.h and j6.m = j0.m and j6.d = 5
order by 1

