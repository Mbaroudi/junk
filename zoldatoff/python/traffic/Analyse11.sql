create table z150__hm as
select h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length between 0 and 150
group by h, m;

create table z150_wd_hm as
select d%7 wd, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length between 0 and 150
group by d%7, h, m;

create table z150_ as
select j.edge_group, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length between 0 and 150
group by j.edge_group;

create table z150_hm as
select j.edge_group, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length between 0 and 150
group by j.edge_group, h, m;

###########################

create table z300__hm as
select h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length between 150 and 300
group by h, m;

create table z300_wd_hm as
select d%7 wd, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length between 150 and 300
group by d%7, h, m;

create table z300_ as
select j.edge_group, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length between 150 and 300
group by j.edge_group;

create table z300_hm as
select j.edge_group, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length between 150 and 300
group by j.edge_group, h, m;

###########################

create table z3000__hm as
select h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length > 300
group by h, m;

create table z3000_wd_hm as
select d%7 wd, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length > 300
group by d%7, h, m;

create table z3000_ as
select j.edge_group, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length > 300
group by j.edge_group;

create table z3000_hm as
select j.edge_group, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0 j inner join edge_data e on j.edge_group = e.edge_group
where d%7 not in (1,2) and e.length > 300
group by j.edge_group, h, m;

##########################################

create table task_80_all as	 
select r.h, r.m,
	   round(avg(
			case 
  			 when  hm150.jam_speed is not null and  hm150.cnt>9 then  hm150.jam_speed-2
  			 when  hm300.jam_speed is not null and  hm300.cnt>5 then  hm300.jam_speed-3
  			 when hm3000.jam_speed is not null and hm3000.cnt>3 then hm3000.jam_speed
  			 when  e150.jam_speed is not null and  e150.cnt>1 then  e150.jam_speed
  			 when  e300.jam_speed is not null and  e300.cnt>1 then  e300.jam_speed
  			 when e3000.jam_speed is not null and e3000.cnt>1 then e3000.jam_speed
  			 else 55
  			end
  		)) jam_speed
from result0 r
	 left join z150_hm hm150  on r.edge_group = hm150.edge_group and r.h = hm150.h and r.m = hm150.m
	 left join z150_   e150   on r.edge_group =  e150.edge_group
	 left join z300_hm hm300  on r.edge_group = hm300.edge_group and r.h = hm300.h and r.m = hm300.m
	 left join z300_   e300   on r.edge_group =  e300.edge_group
	 left join z3000_hm hm3000  on r.edge_group = hm3000.edge_group and r.h = hm3000.h and r.m = hm3000.m
	 left join z3000_   e3000   on r.edge_group =  e3000.edge_group
group by r.h, r.m;


create table task_80_150 as	 
select r.h, r.m,
	   round(avg(
			case 
  			 when  hm150.jam_speed is not null and  hm150.cnt>9 then  hm150.jam_speed-2
  			 when  e150.jam_speed is not null and  e150.cnt>1 then  e150.jam_speed
  			 else 55
  			end
  		)) jam_speed
from result0 r
	 left join z150_hm hm150  on r.edge_group = hm150.edge_group and r.h = hm150.h and r.m = hm150.m
	 left join z150_   e150   on r.edge_group =  e150.edge_group
group by r.h, r.m;

create table task_80_300 as	 
select r.h, r.m,
	   round(avg(
			case 
  			 when  hm300.jam_speed is not null and  hm300.cnt>5 then  hm300.jam_speed-3
  			 when  e300.jam_speed is not null and  e300.cnt>1 then  e300.jam_speed
  			 else 55
  			end
  		)) jam_speed
from result0 r
	 left join z300_hm hm300  on r.edge_group = hm300.edge_group and r.h = hm300.h and r.m = hm300.m
	 left join z300_   e300   on r.edge_group =  e300.edge_group
group by r.h, r.m;

create table task_80_3000 as	 
select r.h, r.m,
	   round(avg(
			case 
  			 when hm3000.jam_speed is not null and hm3000.cnt>3 then hm3000.jam_speed
  			 when e3000.jam_speed is not null and e3000.cnt>1 then e3000.jam_speed
  			 else 55
  			end
  		)) jam_speed
from result0 r
	 left join z3000_hm hm3000 on r.edge_group = hm3000.edge_group and r.h = hm3000.h and r.m = hm3000.m
	 left join z3000_   e3000  on r.edge_group = e3000.edge_group
group by r.h, r.m;

##############

select hm.h*60+hm.m t,
	   round(mon.jam_speed) mon,
	   round(hm.jam_speed) workday,
	   round(j.jam_speed) real_speed,
	   t.jam_speed provision
from z150__hm hm
	 left join z150_wd_hm mon on mon.h = hm.h and mon.m = hm.m and mon.wd = 3
	 left join (select h, m, avg(jam_speed) jam_speed 
	 			from jams0 j inner join edge_data e on j.edge_group = e.edge_group
	 			where d=31 and length < 150
	 			group by h,m
	 		    ) j on j.h=hm.h and j.m=hm.m
	 left join task_80_150 t on t.h=hm.h and t.m=hm.m;
	 
select hm.h*60+hm.m t,
	   round(mon.jam_speed) mon,
	   round(hm.jam_speed) workday,
	   round(j.jam_speed) real_speed,
	   t.jam_speed provision
from z300__hm hm
	 left join z300_wd_hm mon on mon.h = hm.h and mon.m = hm.m and mon.wd = 3
	 left join (select h, m, avg(jam_speed) jam_speed 
	 			from jams0 j inner join edge_data e on j.edge_group = e.edge_group
	 			where d=31 and length between 150 and 300
	 			group by h,m
	 		    ) j on j.h=hm.h and j.m=hm.m
	 left join task_80_300 t on t.h=hm.h and t.m=hm.m;
	 
select hm.h*60+hm.m t,
	   round(mon.jam_speed) mon,
	   round(hm.jam_speed) workday,
	   round(j.jam_speed) real_speed,
	   t.jam_speed provision
from z3000__hm hm
	 left join z3000_wd_hm mon on mon.h = hm.h and mon.m = hm.m and mon.wd = 3
	 left join (select h, m, avg(jam_speed) jam_speed 
	 			from jams0 j inner join edge_data e on j.edge_group = e.edge_group
	 			where d=31 and length > 300
	 			group by h,m
	 		    ) j on j.h=hm.h and j.m=hm.m
	 left join task_80_3000 t on t.h=hm.h and t.m=hm.m;
	
	
###############################
###############################

create table z_len_speed as
select r.l, 
	   sum(e.length*j.jam_speed)/sum(e.length*j.jam_speed/j.jam_speed) avg_speed, 
	   count(distinct e.edge_group) cnt
from ( 
select 50 l union
select 150 l union
select 250 l union
select 350 l union
select 450 l union
select 550 l union
select 650 l union
select 750 l union
select 850 l union
select 950 l union
select 1050 l union
select 1150 l union
select 1250 l union
select 1350 l union
select 1450 l union
select 1550 l union
select 1650 l union
select 1750 l union
select 1850 l union
select 1950 l union
select 2050 l union
select 2150 l union
select 2250 l union
select 2350 l union
select 2450 l union
select 2550 l union
select 2650 l union
select 2750 l union
select 2850 l
) r
inner join edge_data e on e.length between r.l-50 and r.l+50
inner join jams0 j on j.edge_group = e.edge_group
where d < 31
group by r.l


# 64.942
create table task_80 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when  hm150.jam_speed is not null and  hm150.cnt>7 then  hm150.jam_speed
  			 when  hm300.jam_speed is not null and  hm300.cnt>5 then  hm300.jam_speed
  			 when hm3000.jam_speed is not null and hm3000.cnt>3 then hm3000.jam_speed
  			 when   e150.jam_speed is not null and   e150.cnt>1 then   e150.jam_speed
  			 when   e300.jam_speed is not null and   e300.cnt>1 then   e300.jam_speed
  			 when  e3000.jam_speed is not null and  e3000.cnt>1 then  e3000.jam_speed
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join z150_hm hm150  on r.edge_group = hm150.edge_group and r.h = hm150.h and r.m = hm150.m
	 left join z150_   e150   on r.edge_group =  e150.edge_group
	 left join z300_hm hm300  on r.edge_group = hm300.edge_group and r.h = hm300.h and r.m = hm300.m
	 left join z300_   e300   on r.edge_group =  e300.edge_group
	 left join z3000_hm hm3000  on r.edge_group = hm3000.edge_group and r.h = hm3000.h and r.m = hm3000.m
	 left join z3000_   e3000   on r.edge_group =  e3000.edge_group
	
create table task_81 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when  hm150.jam_speed is not null and  hm150.cnt>7 then  hm150.jam_speed
  			 when  hm300.jam_speed is not null and  hm300.cnt>5 then  hm300.jam_speed
  			 when hm3000.jam_speed is not null and hm3000.cnt>3 then hm3000.jam_speed
  			 when   e150.jam_speed is not null and   e150.cnt>1 then   e150.jam_speed
  			 when   e300.jam_speed is not null and   e300.cnt>1 then   e300.jam_speed
  			 when  e3000.jam_speed is not null and  e3000.cnt>1 then  e3000.jam_speed
  			 when ls.avg_speed is not null then ls.avg_speed
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join z150_hm hm150   on r.edge_group =  hm150.edge_group and r.h = hm150.h and r.m = hm150.m
	 left join z150_   e150    on r.edge_group =   e150.edge_group
	 left join z300_hm hm300   on r.edge_group =  hm300.edge_group and r.h = hm300.h and r.m = hm300.m
	 left join z300_   e300    on r.edge_group =   e300.edge_group
	 left join z3000_hm hm3000 on r.edge_group = hm3000.edge_group and r.h = hm3000.h and r.m = hm3000.m
	 left join z3000_   e3000  on r.edge_group =  e3000.edge_group
	 left join edge_data e	   on e.edge_group = r.edge_group
	 left join z_len_speed ls  on e.length between ls.l-50 and ls.l+50

# # # #####################################################

select r.h*60+r.m, round(
	   avg(case 
  			 when  hm150.jam_speed is not null and  hm150.cnt>7 then  hm150.jam_speed-1
  			 when   e150.jam_speed is not null and   e150.cnt>1 then   e150.jam_speed
  			 when ls.avg_speed is not null then ls.avg_speed
  			 else 55
  			end))
from result0 r
	 left join z150_hm hm150   on r.edge_group =  hm150.edge_group and r.h = hm150.h and r.m = hm150.m
	 left join z150_   e150    on r.edge_group =   e150.edge_group
	 left join edge_data e	   on e.edge_group = r.edge_group
	 left join z_len_speed ls  on e.length between ls.l-50 and ls.l+50
where e.length < 150
group by r.h*60+r.m


select r.h*60+r.m, round(
	   avg(case 
  			 when  hm300.jam_speed is not null and  hm300.cnt>5 then  hm300.jam_speed
  			 when   e300.jam_speed is not null and   e300.cnt>1 then   e300.jam_speed
  			 when ls.avg_speed is not null then ls.avg_speed
  			 else 55
  			end))
from result0 r
	 left join z300_hm hm300   on r.edge_group =  hm300.edge_group and r.h = hm300.h and r.m = hm300.m
	 left join z300_   e300    on r.edge_group =   e300.edge_group
	 left join edge_data e	   on e.edge_group = r.edge_group
	 left join z_len_speed ls  on e.length between ls.l-50 and ls.l+50
where e.length between 150 and 300
group by r.h*60+r.m

select r.h*60+r.m, round(
	   avg(case 
  			 when hm3000.jam_speed is not null and hm3000.cnt>1 then hm3000.jam_speed
  			 when  e3000.jam_speed is not null and  e3000.cnt>1 then  e3000.jam_speed
   			 when ls.avg_speed is not null then ls.avg_speed
  			 else 55
  			end))
from result0 r
	 left join z3000_hm hm3000 on r.edge_group = hm3000.edge_group and r.h = hm3000.h and r.m = hm3000.m
	 left join z3000_   e3000  on r.edge_group =  e3000.edge_group
	 left join edge_data e	   on e.edge_group = r.edge_group
	 left join z_len_speed ls  on e.length between ls.l-50 and ls.l+50
where e.length > 300
group by r.h*60+r.m

# # # #####################################################

