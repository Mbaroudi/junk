#base day = 24

create table n_01 as
select h, m, ifnull(s.edge_group, node_group) edge_group, jam_speed
from (
	select h, m, 
		   case when s.node is null then j.edge_group else -s.node end node_group,
	   	avg(jam_speed) jam_speed	
	from jams0 j
		 inner join s_edges s on s.edge_group = j.edge_group
	where j.d < 24 and j.d%7 = 31%7
	group by h, m, case when s.node is null then j.edge_group else -s.node end
) t
left join s_edges s on -s.node = t.node_group

select h*60+m, round(avg(jam_speed)) from n_01 group by h,m order by 1

select h*60+m, round(avg(jam_speed)) from jams0 where d=24 group by h,m order by 1

create table n_02 as
select j.edge_group, avg(j.jam_speed) - avg(n.jam_speed) ds
from jams0 j
	inner join n_01 n on n.edge_group = j.edge_group
where j.d = 24 
	and 60*j.h+j.m between 17*60+40 and 18*60
	and 60*n.h+n.m between 17*60+40 and 18*60
group by j.edge_group


select sum(e.length/120 * (1+(j.t-24*60*24-18*60-2)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from (
	select r.edge_group,
			r.h, r.m,
			round(ifnull(t.jam_speed, 60)+ifnull(l.ds,0)) jam_speed
	from result0 r
	 	 left join n_01 t on t.h=r.h and t.m=r.m and r.edge_group=t.edge_group
	 	 left join n_02 l on l.edge_group = r.edge_group
	) t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 24
	inner join edge_data e on e.edge_group = t.edge_group
	
	
	

	create table n_03 as 
	select h,m, round(avg(jam_speed)) jam_speed
	from n_01 
	group by h,m


	select t.edge_group, sum(e.length/120 * (1+(j.t-24*60*24-18*60-2)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
	from (
		select r.edge_group,
				r.h, r.m,
				case when t.jam_speed is not null then t.jam_speed+ifnull(l.ds, -10)
					 when n.jam_speed is not null then n.jam_speed-10
					 else 0
				end jam_speed
		from result0 r
		 	 left join n_01 t on t.h=r.h and t.m=r.m and r.edge_group=t.edge_group
		 	 left join n_02 l on l.edge_group = r.edge_group
		 	 left join n_03 n on n.h=r.h and n.m=r.m
		) t
		inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 24
		inner join edge_data e on e.edge_group = t.edge_group
	group by t.`edge_group`order by 2 desc
	limit 200


	select t.h*60+t.m, j.jam_speed, t.jam_speed
	from (
		select r.edge_group,
				r.h, r.m,
				case when t.jam_speed is not null then t.jam_speed+ifnull(l.ds, -10)
					 when n.jam_speed is not null then n.jam_speed-10
					 else 0
				end jam_speed
		from result0 r
		 	 left join n_01 t on t.h=r.h and t.m=r.m and r.edge_group=t.edge_group
		 	 left join n_02 l on l.edge_group = r.edge_group
		 	 left join n_03 n on n.h=r.h and n.m=r.m
		) t
		inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 24
		inner join edge_data e on e.edge_group = t.edge_group
	where t.edge_group = 624111
	order by 1
	
	
	create table n_04 as
	select h, ifnull(s.edge_group, node_group) edge_group, jam_speed
	from (
		select h, 
			   case when s.node is null then j.edge_group else -s.node end node_group,
		   	avg(jam_speed) jam_speed	
		from jams0 j
			 inner join s_edges s on s.edge_group = j.edge_group
		where j.d < 24 and j.d%7 = 31%7
		group by h, case when s.node is null then j.edge_group else -s.node end
	) t
	left join s_edges s on -s.node = t.node_group