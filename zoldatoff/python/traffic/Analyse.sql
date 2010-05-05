create table edge_wd_hm as
select edge_group, d%7 wd, h, m, avg(jam_speed) jam_speed
from jams0
where h >= 18
group by edge_group, d%7, h, m

create table edge_wd_h as
select edge_group, wd, h, avg(jam_speed) jam_speed
from edge_wd_hm
group by edge_group, wd, h

create table edge_wd as
select edge_group, wd, avg(jam_speed) jam_speed
from edge_wd_h
group by edge_group, wd

create table edge_ as
select edge_group, avg(jam_speed) jam_speed
from edge_wd
group by edge_group

	###############################################
	create table edge2_wd_hm as
	select edge_group, d%7 wd, h, m, avg(case when jam_speed>120 then jam_speed-100 else jam_speed end) jam_speed
	from jams0
	where h >= 18
	group by edge_group, d%7, h, m

	create table edge2_wd_h as
	select edge_group, wd, h, avg(jam_speed) jam_speed
	from edge2_wd_hm
	group by edge_group, wd, h

	create table edge2_wd as
	select edge_group, wd, avg(jam_speed) jam_speed
	from edge2_wd_h
	group by edge_group, wd

	create table edge2_ as
	select edge_group, avg(jam_speed) jam_speed
	from edge2_wd
	group by edge_group

	################################################

##########################################
# Расчет результата

create table task_10 as
select r.edge_group,
		concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
		round(
		case when whm.jam_speed is not null then whm.jam_speed
  			  when wh.jam_speed is not null then wh.jam_speed
  			  when w.jam_speed is not null then w.jam_speed
  			  when e.jam_speed is not null then e.jam_speed
  			  else 52
  		end, 0) jam_speed
from result0 r
	  left join edge_wd_hm whm on r.edge_group = whm.edge_group and r.d%7 = whm.wd and r.h = whm.h and r.m = whm.m
	  left join edge_wd_h wh on r.edge_group = wh.edge_group and r.d%7 = wh.wd and r.h = wh.h
	  left join edge_wd w on r.edge_group = w.edge_group and r.d%7 = w.wd
	  left join edge_ e on r.edge_group = e.edge_group

	
create table task_11 as
select r.edge_group,
		concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
		round(
		case #when whm.jam_speed is not null then whm.jam_speed
  			  when wh.jam_speed is not null then wh.jam_speed
  			  when w.jam_speed is not null then w.jam_speed
  			  when e.jam_speed is not null then e.jam_speed
  			  else 52
  		end, 0) jam_speed
from result0 r
	  #left join edge_wd_hm whm on r.edge_group = whm.edge_group and r.d%7 = whm.wd and r.h = whm.h and r.m = whm.m
	  left join edge_wd_h wh on r.edge_group = wh.edge_group and r.d%7 = wh.wd and r.h = wh.h
	  left join edge_wd w on r.edge_group = w.edge_group and r.d%7 = w.wd
	  left join edge_ e on r.edge_group = e.edge_group

##########################################
# Проверка методики

create table tedge_wd_hm as
select edge_group, d%7 wd, h, m, avg(jam_speed) jam_speed
from jams0
where h >= 18 and d < 30
group by edge_group, d%7, h, m

create table tedge_wd_h as
select edge_group, wd, h, avg(jam_speed) jam_speed
from tedge_wd_hm
group by edge_group, wd, h

create table tedge_wd as
select edge_group, wd, avg(jam_speed) jam_speed
from tedge_wd_h
group by edge_group, wd

create table tedge_ as
select edge_group, avg(jam_speed) jam_speed
from tedge_wd
group by edge_group


create table task_t10 as
select r.edge_group,
		r.h, r.m,
		round(
		case when whm.jam_speed is not null then whm.jam_speed
  			  when wh.jam_speed is not null then wh.jam_speed
  			  when w.jam_speed is not null then w.jam_speed
  			  when e.jam_speed is not null then e.jam_speed
  			  else 52
  		end, 0) jam_speed
from result0 r
	  left join tedge_wd_hm whm on r.edge_group = whm.edge_group and (r.d-1)%7 = whm.wd and r.h = whm.h and r.m = whm.m
	  left join tedge_wd_h wh on r.edge_group = wh.edge_group and (r.d-1)%7 = wh.wd and r.h = wh.h
	  left join tedge_wd w on r.edge_group = w.edge_group and (r.d-1)%7 = w.wd
	  left join tedge_ e on r.edge_group = e.edge_group
	
	  
select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from task_t10 t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group
	
	
####################################
create table task_t20 as
select edge_group, h, m, coalesce(s1,s2,s3,s4,s5) jam_speed from (
	select r.edge_group, r.h, r.m,
			sum( (case when (r.d-1)%7 = whm.wd then 1.1 else 1 end) * whm.jam_speed ) 
				/ sum( whm.jam_speed / whm.jam_speed * (case when (r.d-1)%7 = whm.wd then 1.1 else 1 end) ) s1,
			
			sum( (case when (r.d-1)%7 = wh.wd then 1.1 else 1 end) * wh.jam_speed ) 
				/ sum( wh.jam_speed / wh.jam_speed * (case when (r.d-1)%7 = wh.wd then 1.1 else 1 end) ) s2,
			
			sum( (case when (r.d-1)%7 = w.wd then 1.1 else 1 end) * w.jam_speed ) 
				/ sum( w.jam_speed / w.jam_speed * (case when (r.d-1)%7 = w.wd then 1.1 else 1 end) ) s3,
			
			e.jam_speed s4,
		
			52 s5
	from result0 r
		  left join tedge_wd_hm whm on r.edge_group = whm.edge_group and r.h = whm.h and r.m = whm.m
		  left join tedge_wd_h wh on r.edge_group = wh.edge_group and (r.d-1)%7 = wh.wd and r.h = wh.h
		  left join tedge_wd w on r.edge_group = w.edge_group and (r.d-1)%7 = w.wd
		  left join tedge_ e on r.edge_group = e.edge_group
	group by r.edge_group, r.h, r.m
) s
