create table t2_g as
select r.edge_group, r.h, r.m, round(hm.jam_speed-4) jam_speed, j.jam_speed real_speed
from result0 r
	 inner join t2_hm hm on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join jams0 j on j.edge_group = r.edge_group and j.h = r.h and j.m = r.m and j.d = 24
where hm.cnt > 9

create table t2_b as
select r.edge_group, r.h, r.m, round(e.jam_speed-1) jam_speed, j.jam_speed real_speed
from result0 r
	 left join t2_hm hm on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m and hm.cnt > 9
	 left join jams0 j on j.edge_group = r.edge_group and j.h = r.h and j.m = r.m and j.d = 24
	 inner join t2_ e on r.edge_group =  e.edge_group 
where hm.edge_group is null

create table t2_bb as
select r.edge_group, r.h, r.m, 55 jam_speed, j.jam_speed real_speed
from result0 r
	 left join t2_hm hm on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m and hm.cnt > 9
	 left join jams0 j on j.edge_group = r.edge_group and j.h = r.h and j.m = r.m and j.d = 24
	 left join t2_ e on r.edge_group =  e.edge_group 
where hm.edge_group is null and e.edge_group is null

##########################################

select 60*g.h+g.m, 
	round(avg(mon.jam_speed)) mon_speed,
	round(avg(hm.jam_speed)) avg_speed,
	round(avg(g.real_speed)) real_speed,
	round(avg(g.jam_speed)) provision
from t2_g g
	 left join t2_hm hm on g.h = hm.h and g.m = hm.m and hm.edge_group = g.edge_group
	 left join t2_ewdhm mon on mon.h = g.h and mon.m = g.m and mon.wd = 3 and mon.edge_group = g.edge_group
group by g.h, g.m
order by 1


##########################################
##########################################

create table t2_b as
select r.edge_group, r.h, r.m, round(h.jam_speed-3) jam_speed, j.jam_speed real_speed
from result0 r
	 left join t2_hm hm on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m and hm.cnt > 9
	 left join jams0 j on j.edge_group = r.edge_group and j.h = r.h and j.m = r.m and j.d = 24
	 inner join t2_h2 h on r.edge_group = h.edge_group and r.h div 2 = h.h2 and h.cnt > 100
where hm.edge_group is null

create table t2_bb as
select r.edge_group, r.h, r.m, round(e.jam_speed-1) jam_speed, j.jam_speed real_speed
from result0 r
	 left join t2_hm hm on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m and hm.cnt > 9
	 left join jams0 j on j.edge_group = r.edge_group and j.h = r.h and j.m = r.m and j.d = 24
	 left join t2_h2 h on r.edge_group = h.edge_group and r.h div 2 = h.h2 and h.cnt > 100
	 inner join t2_ e on r.edge_group =  e.edge_group and e.cnt > 1
where hm.edge_group is null and h.edge_group is null


select count(distinct edge_group), count(*) from t2_g
union all
select count(distinct edge_group), count(*) from t2_b
union all
select count(distinct edge_group), count(*) from t2_bb

