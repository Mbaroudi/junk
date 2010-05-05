create table t_v0 as
select j0.edge_group, j0.jam_speed
from jams0 j0
	inner join (
		select edge_group, max(t) t
		from jams0
		where d=30 and h < 18
		group by edge_group
	) j1 on j0.edge_group = j1.edge_group and j0.t = j1.t
	
	
create table task_t56 as
select r.edge_group,
		r.h, r.m,
		round(
		case
			 when wh.jam_speed is not null and wh.cnt>10 then wh.jam_speed 
  			 when w.jam_speed  is not null and w.cnt>10 then w.jam_speed
  			 when h.jam_speed  is not null and h.cnt>10 then h.jam_speed 
  			 when e.jam_speed  is not null and e.cnt>10 then e.jam_speed
  			 when t.jam_speed is not null then t.jam_speed
  			 else 59
  		end, 0) jam_speed
from result0 r
	 /*2*/ left join t0_wd_h wh on r.edge_group = wh.edge_group and r.d%7 = wh.wd and r.h = wh.h
	 /*3*/ left join t0_wd w on r.edge_group = w.edge_group and r.d%7 = w.wd
	 /*5*/ left join t0_h h on r.edge_group = h.edge_group and r.h = h.h
	 /*6*/ left join t0_ e on r.edge_group = e.edge_group
	 left join t_v0 t on r.edge_group = t.edge_group
	
	

select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from (
		select r.edge_group,
				r.h, r.m,
				round(
				case
					 #when wh.jam_speed is not null and wh.cnt>25 then wh.jam_speed 
		  			 when w.jam_speed  is not null and w.cnt>12 then w.jam_speed
		  			 when h.jam_speed  is not null and h.cnt>12 then h.jam_speed 
		  			 when e.jam_speed  is not null and e.cnt>12 then e.jam_speed
		  			 else 59
		  		end, 0) jam_speed
		from result0 r
			 /*2*/ #left join t0_wd_h wh on r.edge_group = wh.edge_group and (r.d-1)%7 = wh.wd and r.h = wh.h
			 /*3*/ left join t0_wd w on r.edge_group = w.edge_group and (r.d-1)%7 = w.wd
			 /*5*/ left join t0_h h on r.edge_group = h.edge_group and r.h = h.h
			 /*6*/ left join t0_ e on r.edge_group = e.edge_group
	) t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group
	
	
	
	
##########################################

create table simple_node_start as
select node_start node
from edges
group by node_start
having count(*) = 1

create table simple_node_end as
select node_end node
from edges
group by node_end
having count(*) = 1

create table simple_node as
select s.node from simple_node_start s where s.node in (select e.node from simple_node_end e)

create table edges2 as
select distinct node, edge_group from (
	select n.node, s.edge_group from simple_node n inner join edges s on n.node = s.node_start
	union
	select n.node, e.edge_group from simple_node n inner join edges e on n.node = e.node_end
) e

create table nodes2 as
select e1.node node1, max(e2.node) node2
from edges2 e1 inner join edges2 e2 
		on e1.edge_group = e2.edge_group 
			and e1.node < e2.node
group by e1.node

## Сборка в группы

select count(*) from edges2
union all
select count(*) from edges3
union all
select count(*) from edges4
union all
select count(*) from edges5
union all
select count(*) from edges6
union all
select count(*) from edges7
union all
select count(*) from edges8
union all
select count(*) from edges9


create table edges3 as
select distinct ifnull(n.node2, e.node) node, e.edge_group
from edges2 e
	 left join nodes2 n on n.node1 = e.node
	 
create table nodes3 as
select e1.node node1, max(e2.node) node2
from edges3 e1 inner join edges3 e2 
		on e1.edge_group = e2.edge_group 
			and e1.node < e2.node
group by e1.node

create table edges4 as
select distinct ifnull(n.node2, e.node) node, e.edge_group
from edges3 e
	 left join nodes3 n on n.node1 = e.node
	 
create table nodes4 as
select e1.node node1, max(e2.node) node2
from edges4 e1 inner join edges4 e2 
		on e1.edge_group = e2.edge_group 
			and e1.node < e2.node
group by e1.node
	 
create table edges5 as
select distinct ifnull(n.node2, e.node) node, e.edge_group
from edges4 e
	 left join nodes4 n on n.node1 = e.node
	 
###################

create table nodes5 as
select e1.node node1, max(e2.node) node2
from edges5 e1 inner join edges5 e2 
		on e1.edge_group = e2.edge_group 
			and e1.node < e2.node
group by e1.node
	 
create table edges6 as
select distinct ifnull(n.node2, e.node) node, e.edge_group
from edges5 e
	 left join nodes5 n on n.node1 = e.node
	 
create table nodes6 as
select e1.node node1, max(e2.node) node2
from edges6 e1 inner join edges6 e2 
		on e1.edge_group = e2.edge_group 
			and e1.node < e2.node
group by e1.node
	 
create table edges7 as
select distinct ifnull(n.node2, e.node) node, e.edge_group
from edges6 e
	 left join nodes6 n on n.node1 = e.node
	 
###################

create table nodes7 as
select e1.node node1, max(e2.node) node2
from edges7 e1 inner join edges7 e2 
		on e1.edge_group = e2.edge_group 
			and e1.node < e2.node
group by e1.node
	 
create table edges8 as
select distinct ifnull(n.node2, e.node) node, e.edge_group
from edges7 e
	 left join nodes7 n on n.node1 = e.node

###########
	 
	 
select edge_group from edges8 group by edge_group having count(*) > 1

#!!!!!!!!!!!!!!!!!!
update s_edges set node = 999999+node


### Расчет средних 


create table t1_wd_h as
select ifnull(node,j.edge_group) node, d%7 wd, h, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z j left join s_edges e on j.edge_group = e.edge_group
where d < 30
group by ifnull(node,j.edge_group), d%7, h;

create table t1_wd as
select ifnull(node,j.edge_group) node, d%7 wd, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z j left join s_edges e on j.edge_group = e.edge_group
where d < 30
group by ifnull(node,j.edge_group), d%7;

create table t1_ as
select ifnull(node,j.edge_group) node, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z j left join s_edges e on j.edge_group = e.edge_group
where d < 30
group by ifnull(node,j.edge_group);

create table t1_h as
select ifnull(node,j.edge_group) node, h, avg(case when jam_speed > 120 then jam_speed-1000 else jam_speed end) jam_speed, count(*) cnt
from jams_z j left join s_edges e on j.edge_group = e.edge_group
where d < 30
group by ifnull(node,j.edge_group), h;


# Оценка результата



select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from (
select r.edge_group,
		r.h, r.m,
		round(
		case
			 when wh.jam_speed is not null and wh.cnt>25 then wh.jam_speed 
  			 when w.jam_speed  is not null and w.cnt>12 then w.jam_speed
  			 when h.jam_speed  is not null and h.cnt>12 then h.jam_speed 
  			 when e.jam_speed  is not null and e.cnt>12 then e.jam_speed
  			 else 59
  		end, 0) jam_speed
from result0 r
		left join s_edges s on r.edge_group = s.edge_group
	 	left join t1_wd_h wh on ifnull(s.node,r.edge_group) = wh.node and (r.d-1)%7 = wh.wd and r.h = wh.h
	 	left join t1_wd w on ifnull(s.node,r.edge_group) = w.node and (r.d-1)%7 = w.wd
	 	left join t1_h h on ifnull(s.node,r.edge_group) = h.node and r.h = h.h
	 	left join t1_ e on ifnull(s.node,r.edge_group) = e.node
) t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group
	
	
# Боевые испытания

create table z1_wd_h as
select ifnull(node,j.edge_group) node, d%7 wd, h, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z j left join s_edges e on j.edge_group = e.edge_group
group by ifnull(node,j.edge_group), d%7, h;

create table z1_wd as
select ifnull(node,j.edge_group) node, d%7 wd, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z j left join s_edges e on j.edge_group = e.edge_group
group by ifnull(node,j.edge_group), d%7;

create table z1_ as
select ifnull(node,j.edge_group) node, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams_z j left join s_edges e on j.edge_group = e.edge_group
group by ifnull(node,j.edge_group);

create table z1_h as
select ifnull(node,j.edge_group) node, h, avg(case when jam_speed > 120 then jam_speed-1000 else jam_speed end) jam_speed, count(*) cnt
from jams_z j left join s_edges e on j.edge_group = e.edge_group
group by ifnull(node,j.edge_group), h;



create table task_46 as
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
		left join s_edges s on r.edge_group = s.edge_group
	 	left join t1_wd_h wh on ifnull(s.node,r.edge_group) = wh.node and r.d%7 = wh.wd and r.h = wh.h
	 	left join z1_wd w on ifnull(s.node,r.edge_group) = w.node and r.d%7 = w.wd
	 	left join z1_h h on ifnull(s.node,r.edge_group) = h.node and r.h = h.h
	 	left join z1_ e on ifnull(s.node,r.edge_group) = e.node
	
# Проверка одинаковости скоростей для взаимосвязанных дорог

select j.t,
	max(case when j.edge_group = 367408 then j.jam_speed else 0 end),
	max(case when j.edge_group = 562853 then j.jam_speed else 0 end),
	max(case when j.edge_group = 650095 then j.jam_speed else 0 end),
	max(case when j.edge_group = 650555 then j.jam_speed else 0 end),
	max(case when j.edge_group = 739198 then j.jam_speed else 0 end)
from jams0 j inner join s_edges n on n.edge_group = j.edge_group
where n.node= 1405237
group by j.t
order by 1

# Хитрожопейшая проверка для 30-го дня с использованием групп улиц

select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from (
select r.edge_group,
		r.h, r.m,
		round(
		case
			 when wh0.jam_speed is not null and wh0.cnt>10 then wh0.jam_speed 
			 #when wh.jam_speed is not null and wh.cnt>10 then wh.jam_speed 
			 
  			 when w0.jam_speed  is not null and w0.cnt>10 then w0.jam_speed
  			 when wh.jam_speed is not null and wh.cnt>10 then wh.jam_speed 
  			 #when w.jam_speed  is not null and w.cnt>10 then w.jam_speed
  			 
  			 when h0.jam_speed  is not null and h0.cnt>10 then h0.jam_speed 
  			 when h.jam_speed  is not null and h.cnt>10 then h.jam_speed 
  			 
  			 when e0.jam_speed  is not null and e0.cnt>10 then e0.jam_speed
  			 when e.jam_speed  is not null and e.cnt>10 then e.jam_speed
  			 else 59
  		end, 0) jam_speed
from result0 r
		left join s_edges s on r.edge_group = s.edge_group
	 	left join t1_wd_h wh on ifnull(s.node,r.edge_group) = wh.node and (r.d-1)%7 = wh.wd and r.h = wh.h
	 	left join t1_wd w on ifnull(s.node,r.edge_group) = w.node and (r.d-1)%7 = w.wd
	 	left join t1_h h on ifnull(s.node,r.edge_group) = h.node and r.h = h.h
	 	left join t1_ e on ifnull(s.node,r.edge_group) = e.node
	 	
	 	left join t0_wd_h wh0 on r.edge_group = wh0.edge_group and (r.d-1)%7 = wh0.wd and r.h = wh0.h
	 	left join t0_wd w0 on r.edge_group = w0.edge_group and (r.d-1)%7 = w0.wd
	 	left join t0_h h0 on r.edge_group = h0.edge_group and r.h = h0.h
	 	left join t0_ e0 on r.edge_group = e0.edge_group
) t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group
	
	
