	drop table task_52_; 

	create table task_52_ as	 
	select r.h, r.m,
		   round(avg(
				case 
	  			 when hm.jam_speed is not null and hm.cnt>10 then hm.jam_speed+1
	  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
	  			 else 55
	  			end
	  		)) jam_speed
	from result0 r
		 left join z2_hm hm  on r.edge_group = hm.edge_group and 
		 	case when r.h*60+r.m+24 < 22*60 then r.h*60+r.m+24 = hm.h*60+hm.m else 21*60+58=hm.h*60+hm.m end
		 left join z2_   e   on r.edge_group =  e.edge_group
	group by r.h, r.m;

	select hm.h*60+hm.m t,
		   round(mon.jam_speed) mon,
		   round(hm.jam_speed) workday,
		   round(j.jam_speed) real_speed,
		   t.jam_speed provision
	from z2__hm hm
		 left join z2_wd_hm mon on mon.h = hm.h and mon.m = hm.m and mon.wd = 3
		 left join (select h, m, avg(jam_speed) jam_speed from jams0 where d=31 group by h,m) j on j.h=hm.h and j.m=hm.m
		 left join task_52_ t on t.h=hm.h and t.m=hm.m
	order by 1;
	
	
#65.641	
create table task_52 as	 
select r.edge_group,
	   concat(r.d+10, " ", r.h, case when r.m<10 then ":0" else ":" end, r.m) dtime,
	   round(
			case 
  			 when hm.jam_speed is not null and hm.cnt>9 then hm.jam_speed+1
  			 when  e.jam_speed is not null and  e.cnt>1 then  e.jam_speed
  			 else 55
  			end
  		) jam_speed
from result0 r
	 left join z2_hm hm  on r.edge_group = hm.edge_group and 
	 	case when r.h*60+r.m+24 < 22*60 then r.h*60+r.m+24 = hm.h*60+hm.m else 21*60+58=hm.h*60+hm.m end
	 left join z2_   e   on r.edge_group =  e.edge_group
	
	
	
###########################################

select sum(j.length/120 * (1+(j.t-35642)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from #60.86
(select r.edge_group,
		r.h, r.m,
		round(
		case 
			 when w.jam_speed is not null and w.cnt>1 then w.jam_speed-5
  			 when hm.jam_speed is not null and hm.cnt>9 then hm.jam_speed-2
  			 when  e.jam_speed is not null and e.cnt>1 then  e.jam_speed
  			 else 55
  		end, 0) jam_speed
from result0 r
	 left join t2_ewdhm w on r.edge_group = w.edge_group and r.h*60+r.m = w.h*60+w.m+12 and w.wd = 3
	 left join t2_hm hm  on r.edge_group = hm.edge_group and r.h*60+r.m = hm.h*60+hm.m+12
	 left join t2_   e   on r.edge_group =  e.edge_group
) t
	inner join jams0_24 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m