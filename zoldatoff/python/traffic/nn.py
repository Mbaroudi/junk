from math import tanh
from pysqlite2 import dbapi2 as sqlite

class searchnet: 
    def __init__(self,dbname):
        self.con=sqlite.connect(dbname)
        
    def __del__(self): 
        self.con.close()

    def maketables(self): 
        self.con.execute('create table hiddennode(create_key)') 
        self.con.execute('create table wordhidden(fromid,toid,strength)') 
        self.con.execute('create table hiddenurl(fromid,toid,strength)') 
        self.con.commit()
        
    def getstrength(self,fromid,toid,layer): 
        if layer==0: table='wordhidden' 
        else: table='hiddenurl' 
        res=self.con.execute('select strength from {0} where fromid={1} and toid={2}'.format(table,fromid,toid)).fetchone( ) 

        if res==None:
            if layer==0: return -0.2
            if layer==1: return 0 
            
        return res[0]
    
    def setstrength(self,fromid,toid,layer,strength): 
        if layer==0: table='wordhidden' 
        else: table='hiddenurl'
        
        res=self.con.execute('select rowid from {0} where fromid={1} and toid={2}'.format(table,fromid,toid)).fetchone( )
        
        if res==None: 
            self.con.execute('insert into {0} (fromid,toid,strength) values ({1},{2},{3})' % (table,fromid,toid,strength)) 
        else:
            rowid=res[0]
            self.con.execute('update {0} set strength={1} where rowid={2}'.format(table,strength,rowid))
            
    def generatehiddennode(self,wordids,urls): 
        if len(wordids)>3: return None 
        createkey='_'.join(sorted([str(wi) for wi in wordids])) 
        res=self.con.execute( "select rowid from hiddennode where create_key='{0}'".format(createkey)).fetchone( )

        if res==None:
            cur=self.con.execute( "insert into hiddennode (create_key) values ('{0}')".format(createkey)) 
            hiddenid=cur.lastrowid
             
            for wordid in wordids:
                self.setstrength(wordid,hiddenid,0,1.0/len(wordids))
                 
            for urlid in urls:
                self.setstrength(hiddenid,urlid,1,0.1) 
                self.con.commit( )