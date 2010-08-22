select h*60+m,
	round(max(case when wd=0 then jam_speed else null end)) s0,
	round(max(case when wd=1 then jam_speed else null end)) s1,
	round(max(case when wd=2 then jam_speed else null end)) s2,
	round(max(case when wd=3 then jam_speed else null end)) s3,
	round(max(case when wd=4 then jam_speed else null end)) s4,
	round(max(case when wd=5 then jam_speed else null end)) s5,
	round(max(case when wd=6 then jam_speed else null end)) s6
from z0__hm
group by h,m
order by 1


select z.h*60+z.m,
	round(max(case when wd=0 then z.jam_speed else null end)) s0,
	round(max(case when wd=1 then z.jam_speed else null end)) s1,
	round(max(case when wd=2 then z.jam_speed else null end)) s2,
	round(max(case when wd=3 then z.jam_speed else null end)) s3,
	round(max(case when wd=4 then z.jam_speed else null end)) s4,
	round(max(case when wd=5 then z.jam_speed else null end)) s5,
	round(max(case when wd=6 then z.jam_speed else null end)) s6,
	round(avg(case when wd not in (1,2) then z.jam_speed else null end)) sw,
	round(avg(j.jam_speed)) real_speed
from z0__hm z
	left join jams_z j on j.d = 24 and j.h = z.h and z.m = j.m
group by z.h,z.m
order by 1

# 1=sat 2=sun

create table t1_ as
select edge_group, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
where d < 24 and d%7 not in (1,2)
group by edge_group;

create table t1_h as
select edge_group, h, avg(case when jam_speed > 120 then jam_speed-1000 else jam_speed end) jam_speed, count(*) cnt
from jams_z
where d < 24 and d%7 not in (1,2)
group by edge_group, h;

create table t1_hm as
select edge_group, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z
where d < 24 and d%7 not in (1,2)
group by edge_group, h, m;


select sum(e.length/120 * (1+(j.t-35642)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from #63.79
(select r.edge_group,
		r.h, r.m,
		round(-4+
		case 
  			 when hm.jam_speed is not null and hm.cnt>1 then hm.jam_speed
  			 when  h.jam_speed is not null and  h.cnt>1 then  h.jam_speed 
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  		end, 0) jam_speed
from result0 r
	 /*3*/ left join t1_hm hm on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 /*5*/ left join t1_h  h  on r.edge_group =  h.edge_group and r.h = h.h
	 /*6*/ left join t1_   e  on r.edge_group =  e.edge_group
) t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 24
	inner join edge_data e on e.edge_group = t.edge_group