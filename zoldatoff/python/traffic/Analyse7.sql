create table t2_ as
select edge_group, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2) and d<24
group by edge_group;

create table t2_h as
select edge_group, h, avg(case when jam_speed > 120 then jam_speed-1000 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2)
group by edge_group, h;

create table t2_hm as
select edge_group, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2) and d<24
group by edge_group, h, m;

create table t2__hm as
select h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2) and d<24
group by h, m;

create table t2_dhm as
select d, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2) and d<24
group by d, h, m;

create table t2_wd_hm as
select d%7 wd, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2) and d<24
group by d%7, h, m;

/*
create table t2_ewdhm as
select edge_group, d%7 wd, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2) and d<24
group by edge_group, d%7, h, m;
*/

create table t2_ewdh as
select edge_group, d%7 wd, h, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2) and d<24
group by edge_group, d%7, h;


select hm.h*60+hm.m t,
	   #round(d3.jam_speed) s3,
	   #round(d4.jam_speed) s4,
	   #round(d5.jam_speed) s5,
	   #round(d6.jam_speed) s6,
	   #round(d7.jam_speed) s7,
	   #round(d10.jam_speed) s10,
	   #round(d11.jam_speed) s11,
	   #round(d12.jam_speed) s12,
	   #round(d13.jam_speed) s13,
	   #round(d14.jam_speed) s14,
	   #round(d17.jam_speed) s17,
	   #round(d18.jam_speed) s18,
	   #round(d19.jam_speed) s19,
	   #round(d20.jam_speed) s20,
	   #round(d21.jam_speed) s21,
	   round(mon.jam_speed) mon,
	   round(tue.jam_speed) tue,
	   round(wed.jam_speed) wed,
	   round(thu.jam_speed) thu,
	   round(fri.jam_speed) fri,
	   round(hm.jam_speed) workday,
	   round(j.jam_speed) real_speed
from t2__hm hm
	 left join t2_dhm d3  on d3.h=hm.h  and d3.m=hm.m  and d3.d=3
	 left join t2_dhm d4  on d4.h=hm.h  and d4.m=hm.m  and d4.d=4
	 left join t2_dhm d5  on d5.h=hm.h  and d5.m=hm.m  and d5.d=5
	 left join t2_dhm d6  on d6.h=hm.h  and d6.m=hm.m  and d6.d=6
	 left join t2_dhm d7  on d7.h=hm.h  and d7.m=hm.m  and d7.d=7
	 left join t2_dhm d10 on d10.h=hm.h and d10.m=hm.m and d10.d=10
	 left join t2_dhm d11 on d11.h=hm.h and d11.m=hm.m and d11.d=11
	 left join t2_dhm d12 on d12.h=hm.h and d12.m=hm.m and d12.d=12
	 left join t2_dhm d13 on d13.h=hm.h and d13.m=hm.m and d13.d=13
	 left join t2_dhm d14 on d14.h=hm.h and d14.m=hm.m and d14.d=14
	 left join t2_dhm d17 on d17.h=hm.h and d17.m=hm.m and d17.d=17
	 left join t2_dhm d18 on d18.h=hm.h and d18.m=hm.m and d18.d=18
	 left join t2_dhm d19 on d19.h=hm.h and d19.m=hm.m and d19.d=19
	 left join t2_dhm d20 on d20.h=hm.h and d20.m=hm.m and d20.d=20
	 left join t2_dhm d21 on d21.h=hm.h and d21.m=hm.m and d21.d=21
	 left join t2_wd_hm mon on mon.h = hm.h and mon.m = hm.m and mon.wd = 3
	 left join t2_wd_hm tue on tue.h = hm.h and tue.m = hm.m and tue.wd = 4
	 left join t2_wd_hm wed on wed.h = hm.h and wed.m = hm.m and wed.wd = 5
	 left join t2_wd_hm thu on thu.h = hm.h and thu.m = hm.m and thu.wd = 6
	 left join t2_wd_hm fri on fri.h = hm.h and fri.m = hm.m and fri.wd = 0
	 left join (select h, m, avg(jam_speed) jam_speed from jams0 where d=24 group by h,m) j on j.h=hm.h and j.m=hm.m



# Подбор

	create table jams0_24 as 
	select j.edge_group, j.t, j.h, j.m, j.jam_speed, e.length
	from jams0 j
		 inner join edge_data e on e.edge_group = j.edge_group
	where j.d = 24
	
select sum(j.length/120 * (1+(j.t-35642)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from #60.86
(select r.edge_group,
		r.h, r.m,
		round(
		case 
  			 when hm.jam_speed is not null and hm.cnt>9 then hm.jam_speed-4
  			 when  e.jam_speed is not null and e.cnt>1 then  e.jam_speed-1
  			 else 55
  		end, 0) jam_speed
from result0 r
	 left join t2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join t2_   e   on r.edge_group =  e.edge_group
) t
	inner join jams0_24 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m

# Анализ

select 
		r.h*60+r.m,
		round(
		case 
  			 when hm.jam_speed is not null and hm.cnt>9 then hm.jam_speed-4
  			 when  e.jam_speed is not null and e.cnt>1 then  e.jam_speed-1
  			 else 55
  		end, 0) jam_speed,
  		j.jam_speed real_speed
from result0 r
	 left join t2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join t2_   e   on r.edge_group =  e.edge_group
	 left join jams0_24 j on j.edge_group = r.edge_group and j.h=r.h and j.m=r.m
where r.edge_group = 837722





#########################################
#########################################

create table t2_h2 as
select edge_group, h div 2 h2, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2) and d<24
group by edge_group, h div 2;


select sum(j.length/120 * (1+(j.t-35642)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from #60.50
(select r.edge_group,
		r.h, r.m,
		round(
		case 
  			 when hm.jam_speed is not null and hm.cnt>10 then hm.jam_speed-4
  			 when h.jam_speed is not null and h.cnt > 100 then h.jam_speed-3
  			 when  e.jam_speed is not null and e.cnt>1 then  e.jam_speed-1
  			 else 33
  		end, 0) jam_speed
from result0 r
	 left join t2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join t2_h2 h on r.edge_group = h.edge_group and r.h div 2 = h.h2 
	 left join t2_   e   on r.edge_group =  e.edge_group
) t
	inner join jams0_24 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m




select sum(j.length/120 * (1+(j.t-35642)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from #60.43
(select r.edge_group,
		r.h, r.m,
		round(
		case 
  			 when hm.jam_speed is not null and hm.cnt>9 then hm.jam_speed-(60*r.h+r.m-1082)/240*6
  			 when  e.jam_speed is not null and e.cnt>1 then  e.jam_speed-1
  			 else 55
  		end, 0) jam_speed
from result0 r
	 left join t2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join t2_   e   on r.edge_group =  e.edge_group
) t
	inner join jams0_24 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m

