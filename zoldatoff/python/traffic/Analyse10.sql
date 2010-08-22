create table z2_dhm as
select d, h, m, avg(case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
from jams0
where d%7 not in (1,2)
group by d, h, m;

select hm.h*60+hm.m t,
	   round(d3.jam_speed-4) s3,
	   round(d4.jam_speed-2) s4,
	   round(d5.jam_speed-2) s5,
	   round(d6.jam_speed-1) s6,
	   round(d7.jam_speed+1) s7,
	   round(d10.jam_speed-5) s10,
	   round(d11.jam_speed-3) s11,
	   round(d12.jam_speed) s12,
	   round(d13.jam_speed-1) s13,
	   ##round(d14.jam_speed) s14,
	   ##round(d17.jam_speed-3) s17,
	   ##round(d18.jam_speed+3) s18,
	   round(d19.jam_speed) s19,
	   round(d20.jam_speed+2) s20,
	   round(d21.jam_speed+4) s21,
	   ##round(d24.jam_speed+3) s24,
	   round(d25.jam_speed+4) s25,
	   round(d26.jam_speed+3) s26,
	   round(d27.jam_speed+3) s27,
	   round(d28.jam_speed+6) s28,
	   round(j.jam_speed) real_speed
from z2__hm hm
	 left join z2_dhm d3  on d3.h=hm.h  and d3.m=hm.m  and d3.d=3
	 left join z2_dhm d4  on d4.h=hm.h  and d4.m=hm.m  and d4.d=4
	 left join z2_dhm d5  on d5.h=hm.h  and d5.m=hm.m  and d5.d=5
	 left join z2_dhm d6  on d6.h=hm.h  and d6.m=hm.m  and d6.d=6
	 left join z2_dhm d7  on d7.h=hm.h  and d7.m=hm.m  and d7.d=7
	 left join z2_dhm d10 on d10.h=hm.h and d10.m=hm.m and d10.d=10
	 left join z2_dhm d11 on d11.h=hm.h and d11.m=hm.m and d11.d=11
	 left join z2_dhm d12 on d12.h=hm.h and d12.m=hm.m and d12.d=12
	 left join z2_dhm d13 on d13.h=hm.h and d13.m=hm.m and d13.d=13
	 left join z2_dhm d14 on d14.h=hm.h and d14.m=hm.m and d14.d=14
	 left join z2_dhm d17 on d17.h=hm.h and d17.m=hm.m and d17.d=17
	 left join z2_dhm d18 on d18.h=hm.h and d18.m=hm.m and d18.d=18
	 left join z2_dhm d19 on d19.h=hm.h and d19.m=hm.m and d19.d=19
	 left join z2_dhm d20 on d20.h=hm.h and d20.m=hm.m and d20.d=20
	 left join z2_dhm d21 on d21.h=hm.h and d21.m=hm.m and d21.d=21
	 left join z2_dhm d24 on d24.h=hm.h and d24.m=hm.m and d24.d=24
	 left join z2_dhm d25 on d25.h=hm.h and d25.m=hm.m and d25.d=25
	 left join z2_dhm d26 on d26.h=hm.h and d26.m=hm.m and d26.d=26
	 left join z2_dhm d27 on d27.h=hm.h and d27.m=hm.m and d27.d=27
	 left join z2_dhm d28 on d28.h=hm.h and d28.m=hm.m and d28.d=28
	 left join (select h, m, avg(jam_speed) jam_speed from jams0 where d=31 group by h,m) j on j.h=hm.h and j.m=hm.m
	
	create table z_delta as
		 select 3 d, -4 ds
		 union
		 select 4 d, -2 ds
		 union
		 select 5 d, -2 ds
		 union
		 select 6 d, -1 ds
		 union
		 select 7 d, 1 ds
		 union
		 select 10 d, -5 ds
		 union
		 select 11 d, -3 ds
		 union
		 select 12 d, 0 ds
		 union
		 select 13 d, -1 ds
		 union
		 select 19 d, 0 ds
		 union
		 select 20 d, 2 ds
		 union
		 select 21 d, 4 ds
		 union
		 select 25 d, 4 ds
		 union
		 select 26 d, 3 ds
		 union
		 select 27 d, 3 ds
		 union
		 select 28 d, 6 ds
		
		create table z3__hm as
		select h, m, avg(ds + case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
		from jams0 j inner join z_delta d on d.d = j.d
		group by h, m;

		create table z3_wd_hm as
		select d.d%7 wd, h, m, avg(ds+case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
		from jams0 j inner join z_delta d on d.d = j.d
		group by d.d%7, h, m;

		create table z3_ as
		select edge_group, avg(ds + case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
		from jams0 j inner join z_delta d on d.d = j.d
		group by edge_group;

		create table z3_hm as
		select edge_group, h, m, avg(ds + case when jam_speed > 120 then jam_speed-100 else jam_speed end) jam_speed, count(*) cnt
		from jams0 j inner join z_delta d on d.d = j.d
		group by edge_group, h, m;
		
		
		create table task_70_ as	 
		select r.h, r.m,
			   round(avg(
					case 
		  			 when hm.jam_speed is not null and hm.cnt>5 then hm.jam_speed
		  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
		  			 else 55
		  			end
		  		)) jam_speed
		from result0 r
			 left join z3_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
			 left join z3_   e   on r.edge_group =  e.edge_group
		group by r.h, r.m;

		select hm.h*60+hm.m t,
			   round(mon.jam_speed) mon,
			   round(hm.jam_speed) workday,
			   round(j.jam_speed) real_speed,
			   t.jam_speed provision
		from z3__hm hm
			 left join z3_wd_hm mon on mon.h = hm.h and mon.m = hm.m and mon.wd = 3
			 left join (select h, m, avg(jam_speed) jam_speed from jams0 where d=31 group by h,m) j on j.h=hm.h and j.m=hm.m
			 left join task_70_ t on t.h=hm.h and t.m=hm.m;

# 65.54
		create table task_70 as	 
		select r.edge_group,
			   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
			   round(
					case 
		  			 when hm.jam_speed is not null and hm.cnt>1 then hm.jam_speed
		  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
		  			 else 55
		  			end
		  		) jam_speed
		from result0 r
			 left join z3_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
			 left join z3_   e   on r.edge_group =  e.edge_group
			
# 65.283592
create table task_71 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when hm.jam_speed is not null and hm.cnt>5 then hm.jam_speed-1
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join z3_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join z3_   e   on r.edge_group =  e.edge_group

# 65.111	
create table task_72 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when hm.jam_speed is not null and hm.cnt>8 then hm.jam_speed-1
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join z3_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join z3_   e   on r.edge_group =  e.edge_group

# 65.304	
create table task_73 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   #round(
			case 
  			 when hm.jam_speed is not null and hm.cnt>8 then hm.jam_speed-2
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  			end
  		 jam_speed
from result0 r
	 left join z3_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join z3_   e   on r.edge_group =  e.edge_group