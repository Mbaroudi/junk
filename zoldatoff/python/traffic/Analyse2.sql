create table tedge2_wd_hm as
select edge_group, d%7 wd, h, m, avg(case when jam_speed>120 then jam_speed-100 else jam_speed end) jam_speed
from jams0
where h >= 18 and d < 30
group by edge_group, d%7, h, m

	create table te2_wd_hm as
	select edge_group, h, m, 
			sum(jam_speed * (case when wd%7 = 30%7 then 5 else 1 end)) 
				/ sum(jam_speed/jam_speed * (case when wd%7 = 30%7 then 5 else 1 end)) jam_speed
	from tedge2_wd_hm
	group by edge_group, h, m

create table tedge2_wd_h as
select edge_group, wd, h, avg(jam_speed) jam_speed
from tedge2_wd_hm
group by edge_group, wd, h

	create table te2_wd_h as
	select edge_group, h, 
			sum(jam_speed * (case when wd%7 = 30%7 then 5 else 1 end)) 
				/ sum(jam_speed/jam_speed * (case when wd%7 = 30%7 then 5 else 1 end)) jam_speed
	from tedge2_wd_h
	group by edge_group, h

create table tedge2_wd as
select edge_group, wd, avg(jam_speed) jam_speed
from tedge2_wd_h
group by edge_group, wd

	create table te2_wd as
	select edge_group, 
			sum(jam_speed * (case when wd%7 = 30%7 then 5 else 1 end)) 
				/ sum(jam_speed/jam_speed * (case when wd%7 = 30%7 then 5 else 1 end)) jam_speed
	from tedge2_wd
	group by edge_group

create table tedge2_ as
select edge_group, avg(jam_speed) jam_speed
from tedge2_wd
group by edge_group

select avg(jam_speed) from tedge2_
select avg(jam_speed) from te2_wd