#!/usr/bin/env python
#from sqlite3 import dbapi2 as sqlite
import _mysql as mysql
import locale

def read_data(con, filename, filetype):
    fh = None
        
    try:
        fh = open(filename, "r")
        print('\nImporting "%s"\n' % filename)
        
        if filetype==0:     #vertices            
            con.query('truncate table vertices')
        elif filetype==1:   #edges
            con.query('truncate table edges')
        elif filetype==2:   #edge_data
            con.query('truncate table edge_data')
        elif filetype==3:   #jams
            con.query('truncate table jams')
        elif filetype==4:   #jams
            con.query('truncate table result')
        else:
            fh.close()
            return False
        
    
        i,j=0,0
        for line in fh:
            try:
                if filetype==0:     #vertices
                    node,node_group=line.split("\t")
                    node,node_group=int(node),int(node_group)
                    con.query('insert into vertices values (%i, %i)' % (node, node_group))
                elif filetype==1:   #edges
                    edge,edge_group,node_start,node_end=line.split("\t")
                    edge,edge_group,node_start,node_end=int(edge),int(edge_group),int(node_start),int(node_end)
                    con.query('insert into edges values (%i, %i, %i, %i)' % (edge,edge_group,node_start,node_end))
                elif filetype==2:   #edge_data
                    edge_group,length,speed=line.split("\t")
                    edge_group,length,speed=int(edge_group),float(length),float(speed)
                    con.query('insert into edge_data values (%i, %f, %f)' % (edge_group,length,speed))
                elif filetype==3:   #jams
                    edge_group,jam_time,jam_speed=line.split("\t")
                    edge_group,jam_speed=int(edge_group),int(jam_speed)
                    
                    d,t=jam_time.split(" ")
                    if int(d)<=31: 
                        jam_timestamp = "2010-01-" + jam_time + ":00"
                    else:
                        jam_timestamp = "2010-02-" + str(int(d)-31) + " " + t + ":00"
                    #h,m=t.split(":")
                    #jam_timestamp=int(d)*24*60 + int(h)*60 + int(m)
                    #print('insert into jams values (%i, `%s`, %i)' % (edge_group,jam_timestamp,jam_speed))
                    con.query('insert into jams values (%i, \"%s\", %i)' % (edge_group,jam_timestamp,jam_speed))
                elif filetype==4:   #result
                    edge_group,jam_time,jam_speed=line.split("\t")
                    edge_group=int(edge_group)
                    
                    d,t=jam_time.split(" ")
                    if int(d)<=31: 
                        jam_timestamp = "2010-01-" + jam_time + ":00"
                    else:
                        jam_timestamp = "2010-02-" + str(int(d)-31) + " " + t + ":00"
                    #h,m=t.split(":")
                    #jam_timestamp=int(d)*24*60 + int(h)*60 + int(m)
                    #print('insert into result values (%i, \"%s\", NULL)' % (edge_group,jam_timestamp))
                    con.query('insert into result values (%i, \"%s\", NULL)' % (edge_group,jam_timestamp))
                    
                i+=1
                if i%10000==0: print('    Loaded %i records' % i)
                
            except Exception as err:
                #print(err)
                j+=1
            
        con.commit()        
        
        print('Loaded %i records' % i)
        if j: print('Failed to load %i records' % j)
        
    except EnvironmentError as err:
        print('Error importing file "%s"' % filename)
        #print(err)
        return False
    
    except Exception as err:
        print(err)
        return False
        
    finally:
        if fh is not None: fh.close() 
        
    return True
        
        
def main(host="localhost",user="traffic", passwd="zaebis",db="traffic"):
    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    
    try:
    
        con=mysql.connect(host=host,user=user, passwd=passwd,db=db)
        con.query('create table if not exists vertices('
                    'node       INTEGER NOT NULL,'
                    'node_group INTEGER NOT NULL, '
                    'PRIMARY KEY (node))')
        con.query('create table if not exists edges(' 
                    'edge       INTEGER NOT NULL,'
                    'edge_group INTEGER NOT NULL,'
                    'node_start INTEGER NOT NULL,'
                    'node_end   INTEGER NOT NULL,'
                    'PRIMARY KEY (edge))')
        con.query('create table if not exists edge_data ('
                    'edge_group INTEGER    NOT NULL,'
                    'length     REAL(7,2)  NOT NULL,'
                    'speed      REAL(5,2)  NOT NULL,'
                    'PRIMARY KEY (edge_group))')
        con.query('create table if not exists jams('
                    'edge_group INTEGER    NOT NULL,'
                    'jam_time   DATETIME   NOT NULL,'
                    'jam_speed  INTEGER    NOT NULL,'
                    'UNIQUE KEY (edge_group,jam_time))')
        
        con.query('create table if not exists result('
                    'edge_group INTEGER    NOT NULL,'
                    'jam_time   DATETIME   NOT NULL,'
                    'jam_speed  INTEGER,'
                    'UNIQUE KEY (edge_group,jam_time))')
       
        
        #read_data(con, 'data/vertices.txt', 0)
        #read_data(con, 'data/edges.txt', 1)
        #read_data(con, 'data/edge_data.txt', 2)
        #read_data(con, 'data/jams.txt', 3)
        read_data(con, 'data/task.txt', 4)
    
    except Exception as err:
        print(err)
        return False
        
    finally:
        if con is not None: con.close()
        
    return True        
     
main()