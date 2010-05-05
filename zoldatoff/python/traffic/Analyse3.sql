# Честное усреднение

drop table if exists jams_z;

create table jams_z as
select edge_group, d, h, m, jam_speed from jams0 where h >= 18;

################################
/*
create table z0_wd_hm as
select edge_group, d%7 wd, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
group by edge_group, d%7, h, m;
*/

create table z0_wd_h as
select edge_group, d%7 wd, h, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
group by edge_group, d%7, h;

create table z0_wd as
select edge_group, d%7 wd, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
group by edge_group, d%7;

create table z0_ as
select edge_group, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
group by edge_group;

/*
create table z0_hm as
select edge_group, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
group by edge_group, h, m;
*/

create table z0_h as
select edge_group, h, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
group by edge_group, h;

################################
/*
create table t0_wd_hm as
select edge_group, d%7 wd, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
where d < 30
group by edge_group, d%7, h, m;
*/
create table t0_wd_h as
select edge_group, d%7 wd, h, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
where d < 30
group by edge_group, d%7, h;

create table t0_wd as
select edge_group, d%7 wd, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
where d < 30
group by edge_group, d%7;

create table t0_ as
select edge_group, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
where d < 30
group by edge_group;
/*
create table t0_hm as
select edge_group, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
where d < 30
group by edge_group, h, m;
*/
create table t0_h as
select edge_group, h, avg(case when jam_speed > 120 then jam_speed-1000 else jam_speed end) jam_speed, count(*) cnt
from jams_z
where d < 30
group by edge_group, h;


##########################
# Тестирование

select avg(jam_speed) from t0_

select sum(j.jam_speed*e.length) / sum(e.length)
from jams_z j inner join edge_data e on j.edge_group = e.edge_group
where j.d < 30

create table task_t40 as
select r.edge_group,
		r.h, r.m,
		round(
		case when whm.jam_speed is not null then whm.jam_speed
  			  when wh.jam_speed is not null then wh.jam_speed
  			  when w.jam_speed is not null then w.jam_speed
  			  
  			  when hm.jam_speed is not null then hm.jam_speed
  			  when h.jam_speed is not null then h.jam_speed
  			  
  			  when e.jam_speed is not null then e.jam_speed
  			  else 49
  		end, 0) jam_speed
from result0 r
	 /*1*/ left join t0_wd_hm whm on r.edge_group = whm.edge_group and (r.d-1)%7 = whm.wd and r.h = whm.h and r.m = whm.m
	 /*2*/ left join t0_wd_h wh on r.edge_group = wh.edge_group and (r.d-1)%7 = wh.wd and r.h = wh.h
	 /*3*/ left join t0_wd w on r.edge_group = w.edge_group and (r.d-1)%7 = w.wd
	  
	 /*4*/ left join t0_hm hm on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 /*5*/ left join t0_h h on r.edge_group = h.edge_group and r.h = h.h
	 
	 /*6*/ left join t0_ e on r.edge_group = e.edge_group
	
create table task_t46 as
select r.edge_group,
		r.h, r.m,
		round(
		case 
  			 when w.jam_speed is not null and w.cnt>5 then w.jam_speed
  			 when h.jam_speed is not null and h.cnt>5 then h.jam_speed 
  			 when e.jam_speed is not null and e.cnt>5 then e.jam_speed
  			 else 49
  		end, 0) jam_speed
from result0 r
	 /*3*/ left join t0_wd w on r.edge_group = w.edge_group and (r.d-1)%7 = w.wd
	 /*5*/ left join t0_h h on r.edge_group = h.edge_group and r.h = h.h
	 /*6*/ left join t0_ e on r.edge_group = e.edge_group
	  

select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from task_t46 t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group
	
# Top расхождений

select t.edge_group, sum(abs(j.jam_speed-t.jam_speed))/count(*) delta
from task_t47 t
	  inner join jams0 j on t.h=j.h and t.m=j.m and j.d=30 and t.edge_group=j.edge_group
group by t.edge_group
order by 2 desc
limit 50

# Пример для анализа

select r.h, r.m,
		r.h*60+r.m t, j.jam_speed real_speed, t.jam_speed calc_speed
from result0 r
	  left join jams0 j on j.h=r.h and j.m=r.m and j.edge_group=r.edge_group and j.d=30
	  left join task_t47 t on t.h=r.h and t.m=r.m and t.edge_group=r.edge_group
where r.edge_group = 649786
order by 1,2

################################################################################################	
# Результат
################################################################################################

create table task_40 as
select r.edge_group,
		concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
		round(
		case 
  			 when w.jam_speed is not null and w.cnt>5 then w.jam_speed
  			 when h.jam_speed is not null and h.cnt>5 then h.jam_speed 
  			 when e.jam_speed is not null and e.cnt>5 then e.jam_speed
  			 else 59
  		end, 0) jam_speed
from result0 r
	 /*3*/ left join z0_wd w on r.edge_group = w.edge_group and r.d%7 = w.wd
	 /*5*/ left join z0_h h on r.edge_group = h.edge_group and r.h = h.h
	 /*6*/ left join z0_ e on r.edge_group = e.edge_group
	
create table task_41 as
select r.edge_group,
		concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
		round(
		case
			 when wh.jam_speed is not null and wh.cnt>10 then wh.jam_speed 
  			 when w.jam_speed  is not null and w.cnt>10 then w.jam_speed
  			 when h.jam_speed  is not null and h.cnt>10 then h.jam_speed 
  			 when e.jam_speed  is not null and e.cnt>10 then e.jam_speed
  			 else 59
  		end, 0) jam_speed
from result0 r
	 /*2*/ left join z0_wd_h wh on r.edge_group = wh.edge_group and r.d%7 = wh.wd and r.h = wh.h
	 /*3*/ left join z0_wd w on r.edge_group = w.edge_group and r.d%7 = w.wd
	 /*5*/ left join z0_h h on r.edge_group = h.edge_group and r.h = h.h
	 /*6*/ left join z0_ e on r.edge_group = e.edge_group