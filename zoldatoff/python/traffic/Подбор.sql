select sum(e.length/120 * (1+(j.t-44282)/4*0.1) * abs(t.jam_speed - j.jam_speed)) / count(*)
from (
select r.edge_group,
		r.h, r.m,
		round(
		case 
			 when tdh.cnt>80 then tdh.jam_speed #43.45
			 when  td.cnt>8  then  td.jam_speed #43.46 
			 when  th.cnt>10 then  th.jam_speed #64.79
  			 when   e.cnt>5  then   e.jam_speed #68.27
  			 else 72
  		end, 0) jam_speed
from result0 r
	 	left join t0_ e       on r.edge_group =   e.edge_group
	 	/**/left join t0_h th on r.edge_group =  th.edge_group and r.h=th.h
	 	left join t0_wd td    on r.edge_group =  td.edge_group and (r.d-1)%7= td.wd
	 	/**/left join t0_wd_h tdh on r.edge_group = tdh.edge_group and (r.d-1)%7=tdh.wd and r.h=tdh.h
) t
	inner join jams0 j on t.edge_group = j.edge_group and t.h = j.h and t.m = j.m and j.d = 30
	inner join edge_data e on e.edge_group = t.edge_group