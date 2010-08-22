
	
	create table t2w_wdhm as
	select t.wd, t.h, t.m, 
		   round(sum(t.jam_speed*e.length)/sum(t.jam_speed/t.jam_speed*e.length)) jam_speed
	from t2_ewdhm t
		 left join edge_data e on e.edge_group = t.edge_group
	group by t.wd, t.h, t.m
	
	
	create table t2w_hm_work as
	select t.h, t.m, 
		   round(sum(t.jam_speed*e.length)/sum(t.jam_speed/t.jam_speed*e.length)) jam_speed
	from t2_ewdhm t
		 left join edge_data e on e.edge_group = t.edge_group
	where t.wd in (3,4,5,6,0)
	group by t.h, t.m
	
	create table t2w_real as
	select t.h, t.m, 
		   round(sum(t.jam_speed*e.length)/sum(t.jam_speed/t.jam_speed*e.length)) jam_speed
	from jams0 t
		 left join edge_data e on e.edge_group = t.edge_group
	where t.d = 24
	group by t.h, t.m
	
	
	select wd.h*60+wd.m t,
		   mon.jam_speed mon,
		   wd.jam_speed workday,
		   j.jam_speed real_speed
#		   t.jam_speed provision
	from t2w_hm_work wd
		 left join t2w_wdhm mon on mon.h = wd.h and mon.m = wd.m and mon.wd = 3
		 left join t2w_real j on j.h=wd.h and j.m=wd.m
#		 left join task_52_ t on t.h=wd.h and t.m=wd.m
	order by 1
	
	
	########################
	
		create table z2w_wdhm as
		select t.d%7 wd, t.h, t.m, 
			   round(sum(t.jam_speed*e.length)/sum(t.jam_speed/t.jam_speed*e.length)) jam_speed
		from jams0 t
			 left join edge_data e on e.edge_group = t.edge_group
		group by t.d%7, t.h, t.m


		create table z2w_hm_work as
		select t.h, t.m, 
			   round(sum(t.jam_speed*e.length)/sum(t.jam_speed/t.jam_speed*e.length)) jam_speed
		from jams0 t
			 left join edge_data e on e.edge_group = t.edge_group
		where t.d%7 in (3,4,5,6,0)
		group by t.h, t.m

		create table z2w_real as
		select t.h, t.m, 
			   round(sum(t.jam_speed*e.length)/sum(t.jam_speed/t.jam_speed*e.length)) jam_speed
		from jams0 t
			 left join edge_data e on e.edge_group = t.edge_group
		where t.d = 31
		group by t.h, t.m


		select wd.h*60+wd.m t,
			   mon.jam_speed mon,
			   wd.jam_speed workday,
			   j.jam_speed real_speed
	#		   t.jam_speed provision
		from z2w_hm_work wd
			 left join z2w_wdhm mon on mon.h = wd.h and mon.m = wd.m and mon.wd = 3
			 left join z2w_real j on j.h=wd.h and j.m=wd.m
	#		 left join task_52_ t on t.h=wd.h and t.m=wd.m
		order by 1