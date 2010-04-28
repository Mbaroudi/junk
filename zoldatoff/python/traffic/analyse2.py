#!/usr/bin/env python

import MySQLdb as mysql
from math import sqrt
import locale

MAX_SHIFT = 7
MAX_DAY = 30
CUT = 30
MIN_T = 45722

def get_data(con, edge_group, d=MAX_DAY):
    cursor = con.cursor()
    cursor.execute("Select ifnull(j.jam_speed, -1) from hm left join jams0 j "
                   "on hm.h=j.h and hm.m=j.m and j.edge_group=%s and j.d=%i "
                   "order by hm.h, hm.m" % (edge_group, d))
    rows = cursor.fetchall()
    s = [float(row[0]) for row in rows]
    ds = []
    v0 = 0
    
    for i in range(1, len(s)):
        if s[i]==-1 or s[i-1]==-1: 
            ds.append(0)
        else:
            ds.append(s[i]-s[i-1]) 
            
        if s[i] != -1: v0 = s[i]
        
    if d==MAX_DAY:
        return ds[:CUT-1], v0
    else:
        return ds, 0

def set_data(con, edge_group, s):
    cursor = con.cursor()
    for i in range(len(s)):
        cursor.execute("INSERT INTO TASK VALUES "
                       "(%i,  %i, %i)" % (edge_group, MIN_T+i*4, s[i]) )

def correlation(s1,s2):
    z = zip(s1,s2)
    S1 = sum(x for x,y in z)
    S2 = sum(y for x,y in z)
    L = float(len(z))
    
    xy = sum(x*y for x,y in z) 
    x_y = S1 * S2 / L
    
    xx = sum(x*x for x,y in z) - S1*S1/L
    yy = sum(y*y for x,y in z) - S2*S2/L
    
    if xx*yy == 0:
        return -1
    else:
        return (xy - x_y) / sqrt(xx*yy)

def analyse(con, edge_group):
    best_corr = -1
    best_shift = 0
    best_day = 0
    best_s = []
    
    s0, v0 = get_data(con, edge_group)
    
    for i in range(1, MAX_DAY):
        s, v = get_data(con, edge_group, i)
        for j in range(-MAX_SHIFT, MAX_SHIFT):
            if j > 0: 
                z = [0 for k in range(j)]
                z += s
            else:
                z = [0 for k in range(-j)]
                z = s[-j:] + z
            
            c = correlation(z, s0)
            if c > best_corr:
                best_corr, best_day, best_shift, best_s = c, i, j, z
    
    x = best_s[CUT:]

    res=[]
    res.append(v0)
    for i in range(1, len(x)+1):
        res.append(res[i-1]+x[i-1])
       
    set_data(con, edge_group, res)

def analyse_all(con):
    cursor = con.cursor()
    cursor.execute("truncate table task")
    cursor.execute("Select distinct edge_group from result0")
    rows = cursor.fetchall()
    
    i = 0
    for row in rows:
        i += 1
        if i%100 == 0: 
            con.commit()
            print("%i edge groups completed" % i)
        analyse(con, row[0])

def main(host="localhost",user="traffic", passwd="zaebis",db="traffic"):
    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    con=mysql.connect(host=host,user=user, passwd=passwd,db=db)
    con.autocommit(0)
    
    analyse_all(con) #467014
    
    con.commit()
    con.close()
    
#main(host="pro.local")
main()