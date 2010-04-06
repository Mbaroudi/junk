#!/usr/bin/env python3.1
from sqlite3 import dbapi2 as sqlite
import locale

def read_data(con, filename, filetype):
    fh = None
        
    try:
        fh = open(filename, "r")
        print('\nImporting "{0}"\n'.format(filename))
        
        if filetype==0:     #vertices            
            con.execute('delete from vertices')
        elif filetype==1:   #edges
            con.execute('delete from edges')
        elif filetype==2:   #edge_data
            con.execute('delete from edge_data')
        elif filetype==3:   #jams
            con.execute('delete from jams')
        else:
            fh.close()
            return False
        
    
        i,j=0,0
        for line in fh:
            try:
                if filetype==0:     #vertices
                    node,node_group=line.split("\t")
                    con.execute('insert into vertices values({0}, {1})'.format(node,node_group))
                elif filetype==1:   #edges
                    edge,edge_group,node_start,node_end=line.split("\t")
                    con.execute('insert into edges values({0}, {1}, {2}, {3})'.format(edge,edge_group,node_start,node_end))
                elif filetype==2:   #edge_data
                    edge_group,length,speed=line.split("\t")
                    con.execute('insert into edge_data values({0}, {1}, {2})'.format(edge_group,length,speed))
                elif filetype==3:   #jams
                    edge_group,jam_time,jam_speed=line.split("\t")
                    d,t=jam_time.split(" ")
                    h,m=t.split(":")
                    jam_timestamp=int(d)*24*60 + int(h)*60 + int(m)
                    con.execute('insert into jams values({0}, {1}, {2})'.format(edge_group,jam_timestamp,jam_speed))
                    
                i+=1
                if i%10000==0: print('    Loaded {0:n} records'.format(i))
            except Exception:
                j+=1
            
        con.commit()        
        
        print('Loaded {0:n} records'.format(i))
        if j: print('Failed to load {0:n} records'.format(j))
        
    except EnvironmentError:
        print('Error importing file "{0}"'.format(filename))
        return False
    finally:
        if fh is not None: fh.close() 
        return True
        
        
def main(dbname="traffic.db"):
    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    
    con=sqlite.connect(dbname)
    con.execute('create table if not exists vertices('
                'node INTEGER(7) UNIQUE,node_group INTEGER(7))')
    con.execute('create table if not exists edges(' 
                'edge INTEGER(7) UNIQUE,edge_group INTEGER(7),node_start INTEGER(7),node_end INTEGER(7))')
    con.execute('create table if not exists edge_data ('
                'edge_group INTEGER(7),length REAL(7,2),speed REAL(5,2))')
    con.execute('create table if not exists jams('
                'edge_group INTEGER(7),jam_time INTEGER(8), jam_speed INTEGER(3))')
    
    read_data(con, 'data/vertices.txt', 0)
    read_data(con, 'data/edges.txt', 1)
    read_data(con, 'data/edge_data.txt', 2)
    read_data(con, 'data/jams.txt', 3)
    
    con.close()
    return True        
     
main()