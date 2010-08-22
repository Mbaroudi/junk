create table task_60 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when hm.jam_speed is not null and hm.cnt>10 then hm.jam_speed-1
  			 when  h.jam_speed is not null and  h.cnt>20 then  h.jam_speed-1
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join z2_hm hm  on r.edge_group = hm.edge_group and r.h = hm.h and r.m = hm.m
	 left join z2_h  h   on r.edge_group =  h.edge_group and r.h =  h.h
	 left join z2_   e   on r.edge_group =  e.edge_group