create table z2__hm as
select h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2)
group by h, m;

create table z2_wd_hm as
select d%7 wd, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2)
group by d%7, h, m;

create table z2_ as
select edge_group, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2)
group by edge_group;

create table z2_hm as
select edge_group, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2)
group by edge_group, h, m;

select hm.h*60+hm.m t,
	   round(mon.jam_speed) mon,
	   round(tue.jam_speed) tue,
	   round(wed.jam_speed) wed,
	   round(thu.jam_speed) thu,
	   round(fri.jam_speed) fri,
	   round(hm.jam_speed) workday,
	   round(j.jam_speed) real_speed
from z2__hm hm
	 left join z2_wd_hm mon on mon.h = hm.h and mon.m = hm.m and mon.wd = 3
	 left join z2_wd_hm tue on tue.h = hm.h and tue.m = hm.m and tue.wd = 4
	 left join z2_wd_hm wed on wed.h = hm.h and wed.m = hm.m and wed.wd = 5
	 left join z2_wd_hm thu on thu.h = hm.h and thu.m = hm.m and thu.wd = 6
	 left join z2_wd_hm fri on fri.h = hm.h and fri.m = hm.m and fri.wd = 0
	 left join (select h, m, avg(jam_speed) jam_speed from jams0 where d=31 group by h,m) j on j.h=hm.h and j.m=hm.m
	
/*	
create table task_50 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when hm.jam_speed is not null and hm.cnt>1 then hm.jam_speed-4
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed-1
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join t2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join t2_   e   on r.edge_group =  e.edge_group
	*/
	
create table task_50_ as	 
select r.h, r.m,
	   round(avg(
			case 
  			 when hm.jam_speed is not null and hm.cnt>1 then hm.jam_speed-2
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  			end
  		)) jam_speed
from result0 r
	 left join z2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join z2_   e   on r.edge_group =  e.edge_group
group by r.h, r.m;

# Analyse	

select hm.h*60+hm.m t,
	   round(mon.jam_speed) mon,
	   round(hm.jam_speed) workday,
	   round(j.jam_speed) real_speed,
	   t.jam_speed provision
from z2__hm hm
	 left join z2_wd_hm mon on mon.h = hm.h and mon.m = hm.m and mon.wd = 3
	 left join (select h, m, avg(jam_speed) jam_speed from jams0 where d=31 group by h,m) j on j.h=hm.h and j.m=hm.m
	 left join task_50_ t on t.h=hm.h and t.m=hm.m;
	
select hm.h*60+hm.m t,
	   round(d3.jam_speed) s3,
	   round(d10.jam_speed) s10,
	   round(d17.jam_speed) s17,
	   round(d24.jam_speed) s24,
 	   round(mon.jam_speed) mon,
	   round(hm.jam_speed) workday,
	   round(j.jam_speed) real_speed,
	   t.jam_speed provision
from t2__hm hm
	 left join z2_dhm d3  on d3.h=hm.h  and d3.m=hm.m  and d3.d=3
	 left join z2_dhm d10 on d10.h=hm.h and d10.m=hm.m and d10.d=10
	 left join z2_dhm d17 on d17.h=hm.h and d17.m=hm.m and d17.d=17
	 left join z2_dhm d24 on d24.h=hm.h and d24.m=hm.m and d24.d=24
	 left join z2_wd_hm mon on mon.h = hm.h and mon.m = hm.m and mon.wd = 3
	 left join (select h, m, avg(jam_speed) jam_speed from jams0 where d=31 group by h,m) j on j.h=hm.h and j.m=hm.m
	 left join task_50_ t on t.h=hm.h and t.m=hm.m;
	
# Result

#65.732050
create table task_50 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when hm.jam_speed is not null and hm.cnt>1 then hm.jam_speed-1
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join z2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join z2_   e   on r.edge_group =  e.edge_group
	
#64.740	
create table task_51 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when hm.jam_speed is not null and hm.cnt>9 then hm.jam_speed-1
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join z2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join z2_   e   on r.edge_group =  e.edge_group
	
#64.719
	create table task_62 as	 
	select r.edge_group,
		   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
		   round(
				case 
	  			 when hm.jam_speed is not null and hm.cnt>10 then hm.jam_speed
	  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
	  			 else 55
	  			end
	  		) jam_speed
	from result0 r
		 left join z2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
		 left join z2_   e   on r.edge_group =  e.edge_group
		
#64.685
create table task_63 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when hm.jam_speed is not null and hm.cnt>9 then hm.jam_speed
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join z2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join z2_   e   on r.edge_group =  e.edge_group