CREATE TABLE task (
  edge_group int(11) NOT NULL,
  t bigint(17) NOT NULL DEFAULT '0',
  jam_speed int(3) not null default '0',
  best_day integer(3),
  best_shift integer(2),
  best_corr double(7,6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8


select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from (
select r.edge_group,
		r.h, r.m,
		round(
		case 
			 when t.best_corr>0 then t.jam_speed
			 when tdh.cnt>80 then tdh.jam_speed #43.45
			 when  td.cnt>8  then  td.jam_speed #43.46 
			 when  th.cnt>10 then  th.jam_speed #64.79
  			 when   e.cnt>5  then   e.jam_speed #68.27
  			 else 72
  		end, 0) jam_speed
from result0 r
	 	left join t0_ e       on r.edge_group =   e.edge_group
	 	/**/left join t0_h th on r.edge_group =  th.edge_group and r.h=th.h
	 	left join t0_wd td    on r.edge_group =  td.edge_group and (r.d-1)%7= td.wd
	 	/**/left join t0_wd_h tdh on r.edge_group = tdh.edge_group and (r.d-1)%7=tdh.wd and r.h=tdh.h
	 	left join task t      on r.edge_group =   t.edge_group and r.t-24*60=t.t
) t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group
	
	



create table t3_1 as select distinct edge_group, h, m from jams_z where d < 30 and d%7 = 30%7 

create table t3_2 as select edge_group, h, m, jam_speed from jams_z where d < 30 and d%7 = 30%7 

create table t3_3 as
select j1.edge_group, j1.h, j1.m, j2.jam_speed, abs((j1.h*60+j1.m)-(j2.h*60+j2.m)) delta
from t3_2 j2 inner join t3_1 j1 on j1.edge_group=j2.edge_group

/*
create table t3_4 as
select edge_group, h, m,
	avg(case when delta < 20 then jam_speed else null end) s20,
	count(case when delta < 20 then jam_speed else null end) c20,
	
	avg(case when delta < 40 then jam_speed else null end) s40,
	count(case when delta < 40 then jam_speed else null end) c40,
	
	avg(case when delta < 60 then jam_speed else null end) s60,
	count(case when delta < 60 then jam_speed else null end) c60,
	
	avg(case when delta < 80 then jam_speed else null end) s80,
	count(case when delta < 80 then jam_speed else null end) c80,
	
	avg(case when delta < 100 then jam_speed else null end) s100,
	count(case when delta < 100 then jam_speed else null end) c100,
	
	avg(case when delta < 120 then jam_speed else null end) s120,
	count(case when delta < 120 then jam_speed else null end) c120,
	
	#avg(case when delta < 140 then jam_speed else null end) s140,
	#count(case when delta < 140 then jam_speed else null end) c140,
	
	#avg(case when delta < 160 then jam_speed else null end) s160,
	#count(case when delta < 160 then jam_speed else null end) c160,
	
	avg(case when delta < 180 then jam_speed else null end) s180,
	count(case when delta < 180 then jam_speed else null end) c180,
	
	#avg(case when delta < 200 then jam_speed else null end) s200,
	#count(case when delta < 200 then jam_speed else null end) c200,

	#avg(case when delta < 220 then jam_speed else null end) s220,
	#count(case when delta < 220 then jam_speed else null end) c220,
	
	avg(case when delta < 240 then jam_speed else null end) s240,
	count(case when delta < 240 then jam_speed else null end) c240
from t3_3
group by edge_group, h, m
*/

create table t3_44 as
select edge_group, h, m,
	avg(case when delta < 20 then jam_speed else null end) s20,
	avg(pow(case when delta < 20 then jam_speed else null end, 2)) sqr20,
	count(case when delta < 20 then jam_speed else null end) c20,
	
	avg(case when delta < 40 then jam_speed else null end) s40,
	avg(pow(case when delta < 40 then jam_speed else null end, 2)) sqr40,
	count(case when delta < 40 then jam_speed else null end) c40,
	
	avg(case when delta < 60 then jam_speed else null end) s60,
	avg(pow(case when delta < 60 then jam_speed else null end, 2)) sqr60,
	count(case when delta < 60 then jam_speed else null end) c60,
	
	avg(case when delta < 80 then jam_speed else null end) s80,
	avg(pow(case when delta < 80 then jam_speed else null end, 2)) sqr80,
	count(case when delta < 80 then jam_speed else null end) c80,
	
	avg(case when delta < 100 then jam_speed else null end) s100,
	avg(pow(case when delta < 100 then jam_speed else null end, 2)) sqr100,
	count(case when delta < 100 then jam_speed else null end) c100,
	
	avg(case when delta < 120 then jam_speed else null end) s120,
	avg(pow(case when delta < 120 then jam_speed else null end, 2)) sqr120,
	count(case when delta < 120 then jam_speed else null end) c120,
	
	#avg(case when delta < 140 then jam_speed else null end) s140,
	#count(case when delta < 140 then jam_speed else null end) c140,
	
	#avg(case when delta < 160 then jam_speed else null end) s160,
	#count(case when delta < 160 then jam_speed else null end) c160,
	
	avg(case when delta < 180 then jam_speed else null end) s180,
	avg(pow(case when delta < 180 then jam_speed else null end, 2)) sqr180,
	count(case when delta < 180 then jam_speed else null end) c180,
	
	#avg(case when delta < 200 then jam_speed else null end) s200,
	#count(case when delta < 200 then jam_speed else null end) c200,

	#avg(case when delta < 220 then jam_speed else null end) s220,
	#count(case when delta < 220 then jam_speed else null end) c220,
	
	avg(case when delta < 240 then jam_speed else null end) s240,
	avg(pow(case when delta < 240 then jam_speed else null end, 2)) sqr240,
	count(case when delta < 240 then jam_speed else null end) c240
from t3_3
group by edge_group, h, m

create table t3_avg as
select edge_group, h, m,
		s20, sqrt(sqr20-pow(s20,2)) d20, c20,
		s40, sqrt(sqr40-pow(s40,2)) d40, c40,
		s60, sqrt(sqr60-pow(s60,2)) d60, c60,
		s80, sqrt(sqr80-pow(s80,2)) d80, c80,
		s100, sqrt(sqr100-pow(s100,2)) d100, c100,
		s120, sqrt(sqr120-pow(s120,2)) d120, c120,
		s180, sqrt(sqr80-pow(s180,2)) d180, c180,
		s240, sqrt(sqr240-pow(s240,2)) d240, c240
from t3_44

/*

create table t3_5 as
select case when e.node is null then t.edge_group else -e.node end edge_node, h, m,
	avg(case when delta < 20 then jam_speed else null end) s20,
	count(case when delta < 20 then jam_speed else null end) c20,
	
	avg(case when delta < 40 then jam_speed else null end) s40,
	count(case when delta < 40 then jam_speed else null end) c40,
	
	avg(case when delta < 60 then jam_speed else null end) s60,
	count(case when delta < 60 then jam_speed else null end) c60,
	
	avg(case when delta < 80 then jam_speed else null end) s80,
	count(case when delta < 80 then jam_speed else null end) c80,
	
	avg(case when delta < 100 then jam_speed else null end) s100,
	count(case when delta < 100 then jam_speed else null end) c100,
	
	avg(case when delta < 120 then jam_speed else null end) s120,
	count(case when delta < 120 then jam_speed else null end) c120,
	
	#avg(case when delta < 140 then jam_speed else null end) s140,
	#count(case when delta < 140 then jam_speed else null end) c140,
	
	#avg(case when delta < 160 then jam_speed else null end) s160,
	#count(case when delta < 160 then jam_speed else null end) c160,
	
	avg(case when delta < 180 then jam_speed else null end) s180,
	count(case when delta < 180 then jam_speed else null end) c180,
	
	#avg(case when delta < 200 then jam_speed else null end) s200,
	#count(case when delta < 200 then jam_speed else null end) c200,

	#avg(case when delta < 220 then jam_speed else null end) s220,
	#count(case when delta < 220 then jam_speed else null end) c220,
	
	avg(case when delta < 240 then jam_speed else null end) s240,
	count(case when delta < 240 then jam_speed else null end) c240
from t3_3 t left join s_edges e on e.edge_group = t.edge_group
group by case when e.node is null then t.edge_group else -e.node end, h, m

create table t3_6 as
select case when t.edge_node < 0 then e.edge_group else t.edge_node end edge_group,
	h, m, s20, c20, s40, c40, s60, c60, s80, c80, s100, c120, s180, c180, s240, c240
from t3_5 t left join s_edges e on -e.node=t.edge_node
*/

create table t3_55 as
select case when e.node is null then t.edge_group else -e.node end edge_node, h, m,
	avg(case when delta < 20 then jam_speed else null end) s20,
	avg(pow(case when delta < 20 then jam_speed else null end, 2)) sqr20,
	count(case when delta < 20 then jam_speed else null end) c20,
	
	avg(case when delta < 40 then jam_speed else null end) s40,
	avg(pow(case when delta < 40 then jam_speed else null end, 2)) sqr40,
	count(case when delta < 40 then jam_speed else null end) c40,
	
	avg(case when delta < 60 then jam_speed else null end) s60,
	avg(pow(case when delta < 60 then jam_speed else null end, 2)) sqr60,
	count(case when delta < 60 then jam_speed else null end) c60,
	
	avg(case when delta < 80 then jam_speed else null end) s80,
	avg(pow(case when delta < 80 then jam_speed else null end, 2)) sqr80,
	count(case when delta < 80 then jam_speed else null end) c80,
	
	avg(case when delta < 100 then jam_speed else null end) s100,
	avg(pow(case when delta < 100 then jam_speed else null end, 2)) sqr100,
	count(case when delta < 100 then jam_speed else null end) c100,
	
	avg(case when delta < 120 then jam_speed else null end) s120,
	avg(pow(case when delta < 120 then jam_speed else null end, 2)) sqr120,
	count(case when delta < 120 then jam_speed else null end) c120,
	
	#avg(case when delta < 140 then jam_speed else null end) s140,
	#count(case when delta < 140 then jam_speed else null end) c140,
	
	#avg(case when delta < 160 then jam_speed else null end) s160,
	#count(case when delta < 160 then jam_speed else null end) c160,
	
	avg(case when delta < 180 then jam_speed else null end) s180,
	avg(pow(case when delta < 180 then jam_speed else null end, 2)) sqr180,
	count(case when delta < 180 then jam_speed else null end) c180,
	
	#avg(case when delta < 200 then jam_speed else null end) s200,
	#count(case when delta < 200 then jam_speed else null end) c200,

	#avg(case when delta < 220 then jam_speed else null end) s220,
	#count(case when delta < 220 then jam_speed else null end) c220,
	
	avg(case when delta < 240 then jam_speed else null end) s240,
	avg(pow(case when delta < 240 then jam_speed else null end, 2)) sqr240,
	count(case when delta < 240 then jam_speed else null end) c240
from t3_3 t left join s_edges e on e.edge_group = t.edge_group
group by case when e.node is null then t.edge_group else -e.node end, h, m

create table t3_avg_mod as
select case when t.edge_node < 0 then e.edge_group else t.edge_node end edge_group,
	h, m,
	s20, sqrt(sqr20-pow(s20,2)) d20, c20,
		s40, sqrt(sqr40-pow(s40,2)) d40, c40,
		s60, sqrt(sqr60-pow(s60,2)) d60, c60,
		s80, sqrt(sqr80-pow(s80,2)) d80, c80,
		s100, sqrt(sqr100-pow(s100,2)) d100, c100,
		s120, sqrt(sqr120-pow(s120,2)) d120, c120,
		s180, sqrt(sqr80-pow(s180,2)) d180, c180,
		s240, sqrt(sqr240-pow(s240,2)) d240, c240
from t3_55 t left join s_edges e on -e.node=t.edge_node




select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from (
select r.edge_group,
		r.h, r.m,
		round(
		case 
			 #when t.d20 < 10 and t.c20 > 10 then t.s20	#
			 #when t.d40 < 4 and t.c40 > 10 then t.s40	#
			 #when t.d60 < 10 and t.c60 > 10 then t.s60	#
			 #when t.d80 < 10 and t.c80 > 10 then t.s80	#
			 #when t.d100 < 10 then t.s100	#
			 #when t.d120 < 10  then t.s120	#
			 #when t.d180 < 10 and t.c180 > 10 then t.s180	#47.7
			 when t.c240 > 10 then t.s240	#47.7
  			 when t.d240 < 40 then t.s240	#47.7
  			 else 72 						#92
  		end, 0) jam_speed
from result0 r
	 	left join t3_avg t on t.h=r.h and t.m=r.m and r.edge_group=t.edge_group
) t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group
	
	
	
	
# Manual comparement of methods

select 60*t.h+t.m t, 
	round(s20), 
	#round(s40), 
	round(s60), 
	#round(s80), 
	#round(s100), 
	round(s120), 
	#round(s180), 
	round(s240),
	j.jam_speed,
	j1.jam_speed,
	tt.jam_speed
from t3_avg t
	left join jams0 j on j.d=30 and t.h=j.h and t.m=j.m and t.edge_group = j.edge_group
	left join jams0 j1 on j1.d=29 and t.h=j1.h and t.m=j1.m and t.edge_group = j1.edge_group
	left join task tt on tt.t=30*60*24+60*t.h+t.m and tt.edge_group=t.edge_group
where t.edge_group = 573459 
order by t.h, t.m

create table zzz2 as
select j.h, j.m, j.edge_group,
		case
		 when abs(j.jam_speed - s20) < d20 then 20
		 when abs(j.jam_speed - s40) < d40 then 40
		 when abs(j.jam_speed - s60) < d60 then 60
		 when abs(j.jam_speed - s80) < d80 then 80
		 when abs(j.jam_speed - s100) < d100 then 100
		 when abs(j.jam_speed - s120) < d120 then 120
		 when abs(j.jam_speed - s180) < d180 then 180
		 when abs(j.jam_speed - s240) < d240 then 240
		else -j.jam_speed
		end	s,
		
		case
		 when abs(j.jam_speed - s20) < d20 then d20
		 when abs(j.jam_speed - s40) < d40 then d40
		 when abs(j.jam_speed - s60) < d60 then d60
		 when abs(j.jam_speed - s80) < d80 then d80
		 when abs(j.jam_speed - s100) < d100 then d100
		 when abs(j.jam_speed - s120) < d120 then d120
		 when abs(j.jam_speed - s180) < d180 then d180
		 when abs(j.jam_speed - s240) < d240 then d240
		else -j.jam_speed
		end	d,
		
		case
		 when abs(j.jam_speed - s20) < d20 then c20
		 when abs(j.jam_speed - s40) < d40 then c40
		 when abs(j.jam_speed - s60) < d60 then c60
		 when abs(j.jam_speed - s80) < d80 then c80
		 when abs(j.jam_speed - s100) < d100 then c100
		 when abs(j.jam_speed - s120) < d120 then c120
		 when abs(j.jam_speed - s180) < d180 then c180
		 when abs(j.jam_speed - s240) < d240 then c240
		else -j.jam_speed
		end	c
from jams0 j
	left join t3_avg_mod t on t.h=j.h and t.m=j.m and t.edge_group = j.edge_group
where j.d=30


# Provision & real data

create table t3_avg2 as
select t.edge_group, t.h, t.m,
		s20,  abs(s20-j.jam_speed) e20,   sqrt(sqr20-pow(s20,2)) d20,    c20,
		s40,  abs(s40-j.jam_speed) e40,   sqrt(sqr40-pow(s40,2)) d40,    c40,
		s60,  abs(s60-j.jam_speed) e60,   sqrt(sqr60-pow(s60,2)) d60,    c60,
		s80,  abs(s80-j.jam_speed) e80,   sqrt(sqr80-pow(s80,2)) d80,    c80,
		s100, abs(s100-j.jam_speed) e100, sqrt(sqr100-pow(s100,2)) d100, c100,
		s120, abs(s120-j.jam_speed) e120, sqrt(sqr120-pow(s120,2)) d120, c120,
		s180, abs(s180-j.jam_speed) e180, sqrt(sqr80-pow(s180,2)) d180,  c180,
		s240, abs(s240-j.jam_speed) e240, sqrt(sqr240-pow(s240,2)) d240, c240
from t3_44 t
	 left join jams0 j on t.edge_group = j.edge_group and t.h=j.h and t.m=j.m and j.d = 30
	
	
	create table zzz3 as
	select
		h, m,
		case when c20 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 20
			 when c40 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 40
			 when c60 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 60
			 when c80 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 80	  	 
			 when c100 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 100
			 when c120 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 120
			 when c180 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 180
			 when c240 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 240 
			 else 0 
	 	end r
	from t3_avg2 t
	where edge_group = 318158 


	create table zzz4
	as
	select h, m, 
		sum(case when r=20 then 1 else 0 end) c20,
		sum(case when r=40 then 1 else 0 end) c40,
		sum(case when r=60 then 1 else 0 end) c60,
		sum(case when r=80 then 1 else 0 end) c80,
		sum(case when r=100 then 1 else 0 end) c100,
		sum(case when r=120 then 1 else 0 end) c120,
		sum(case when r=180 then 1 else 0 end) c180,
		sum(case when r=240 then 1 else 0 end) c240
	from zzz3
	group by h,m


	select * from zzz4 limit 100


	select
		60*h+m,
		case when c20 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 20
			 when c40 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 40
			 when c60 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 60
			 when c80 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 80	  	 
			 when c100 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 100
			 when c120 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 120
			 when c180 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 180
			 when c240 = least(c20, c40, c60, c80, c100, c120, c180, c240) then 240 
			 else 0 
	 	end r
	from zzz4

	create table t3_last as 
	select edge_group, jam_speed from jams0 where d=30 and h=17 and m=58

select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from (
select r.edge_group,
		r.h, r.m,
		round(  #44.56
		case 
			 when r.h*60+r.m between 1082 and 1200 then ifnull(t.s100, 60)
			 when r.h*60+r.m between 1204 and 1318 then ifnull(t.s240, 60)
  			 else 60
  		end, 0) jam_speed
from result0 r
	 	left join t3_avg t on t.h=r.h and t.m=r.m and r.edge_group=t.edge_group
) t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group