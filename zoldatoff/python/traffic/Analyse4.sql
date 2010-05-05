# Взвешенная по дням недели скорость

create table t10_h as
select edge_group, h,
		sum(k*jam_speed)/sum(k*jam_speed/jam_speed) jam_speed,
		count(*) cnt
from
(
	select edge_group, 
			case when d%7=30%7 then 10 else 1 end k, 
			h, 
			case when jam_speed > 120 then jam_speed-100 else jam_speed end jam_speed
	from jams_z
	where d < 30
) s
group by edge_group, h;

create table t10_ as
select edge_group,
		sum(k*jam_speed)/sum(k*jam_speed/jam_speed) jam_speed,
		count(*) cnt
from
(
	select edge_group, 
			case when d%7=30%7 then 10 else 1 end k, 
			case when jam_speed > 120 then jam_speed-100 else jam_speed end jam_speed
	from jams_z
	where d < 30
) s
group by edge_group;

# Проверочная выгрузка

create table task_t50 as
select r.edge_group,
		r.h, r.m,
		round(
		case
			 when h2.jam_speed is not null and h2.cnt>10 then h2.jam_speed 
  			 when h.jam_speed  is not null and h.cnt>10  then h.jam_speed 
  			 when e.jam_speed  is not null and e.cnt>10  then e.jam_speed
  			 else 59
  		end, 0) jam_speed
from result0 r
	 left join t2_h h2 on r.edge_group = h2.edge_group and r.h = h2.h
	 left join t0_h h on r.edge_group = h.edge_group and r.h = h.h
	 left join t0_ e on r.edge_group = e.edge_group
	
# Проверка

select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from task_t46 t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group