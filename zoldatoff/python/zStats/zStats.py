#!/usr/bin/env python
#coding: utf-8

from Datafetch import Twitter
from math import sqrt
from PIL import Image,ImageDraw

import random
import codecs

code = 'utf-8'
FRIEND_COUNT = 50
MESSAGE_COUNT = 100

def getwordstats():
# Collect word statistics
	apcount = {}
	wordcounts = {}
	z = Twitter.Twitter('zoldatoff')
	fiendlist = z.getfriends(FRIEND_COUNT)

	for friend in fiendlist:
		#if friend.screen_name == 'temalebedev': continue
		user, wc = z.getwordcounts(friend, MESSAGE_COUNT)
		wordcounts[user] = wc
		for word, count in wc.items():
			apcount.setdefault(word, 0)
			if count > 1:
				apcount[word] += 1

	wordlist = []
	for w,bc in apcount.items():
		#frac = float(bc) / len(fiendlist)
		#if 0.1 < frac < 0.5:
		wordlist.append(w)

	# Write statistics to file
	out = codecs.open('words.txt','w',code)
	out.write('User')
	for word in wordlist: 
		out.write('\t%s' % word)
	out.write('\n')

	for user, wc in wordcounts.items():
		out.write(user.screen_name)
		for word in wordlist:
			if word in wc: out.write('\t%d' % wc[word])
			else: out.write('\t0')
		out.write('\n')


def readfile(filename):
	lines=[line for line in file(filename)]
	# Первая строка содержит названия столбцов
	colnames=lines[0].strip( ).split('\t')[1:]
	rownames=[]
	data=[]
	for line in lines[1:]:
		p=line.strip( ).split('\t')	
		# Первый столбец в каждой строке содержит название строки
		rownames.append(p[0])
		# Остальные ячейки содержат данные этой строки
		data.append([float(x) for x in p[1:]])
	
	totals = []
	colnumber = len(colnames)
	for i in range(colnumber):
		totals += [sum(1 for k in range(len(rownames)) if data[k][i] > 0)]

	stripdata = []
	stripnames = [colnames[i] for i in range(colnumber) if totals[i] > 5 and len(colnames[i])>6]
	striprows = []
	for i in range(len(rownames)):
		if sum([data[i][k] for k in range(colnumber) if totals[k] > 5 and len(colnames[k])>6]) > 5:
			striprows.append(rownames[i])		
			stripdata.append([data[i][k] for k in range(colnumber) if totals[k] > 5 and len(colnames[k])>6])
		else:
			print 'skipping ', rownames[i]
	 	
	#return rownames,colnames,data
	return striprows,stripnames,stripdata


def pearson(v1,v2):
	# Простые суммы
	sum1=sum(v1)
	sum2=sum(v2)
	
	# Суммы квадратов
	sum1Sq=sum([pow(v,2) for v in v1])
	sum2Sq=sum([pow(v,2) for v in v2])
	
	# Суммы произведений
	pSum=sum([v1[i]*v2[i] for i in range(len(v1))])
	# Вычисляем r (коэффициент Пирсона)
	num=pSum-(sum1*sum2/len(v1))
	den=sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
	if den==0: return 0
	return 1.0-num/den


class bicluster:
	def __init__(self,vec,left=None,right=None,distance=0.0,id=None):
		self.left=left
		self.right=right
		self.vec=vec
		self.id=id
		self.distance=distance


def hcluster(rows,distance=pearson):
	distances={}
	currentclustid=-1
	
	# В начале кластеры совпадают со строками
	clust=[bicluster(rows[i],id=i) for i in range(len(rows))]
	while len(clust)>1:
		lowestpair=(0,1)
		closest=distance(clust[0].vec,clust[1].vec)
		
		# в цикле рассматриваются все пары и ищется пара с минимальным
		# расстоянием
		for i in range(len(clust)):
			for j in range(i+1,len(clust)):
				# вычисленные расстояния запоминаются в кэше
				if (clust[i].id,clust[j].id) not in distances:
					distances[(clust[i].id,clust[j].id)] = distance(clust[i].vec,clust[j].vec)

				d=distances[(clust[i].id,clust[j].id)]
      
			if d<closest:
				closest=d
				lowestpair=(i,j)
    
		# вычислить среднее для двух кластеров
		mergevec=[
		(clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0
		for i in range(len(clust[0].vec))]

		# создать новый кластер
		newcluster=bicluster(mergevec,left=clust[lowestpair[0]],
			right=clust[lowestpair[1]],
			distance=closest,id=currentclustid)

		# идентификаторы кластеров, которых не было в исходном наборе,
		# отрицательны
		currentclustid-=1
		del clust[lowestpair[1]]
		del clust[lowestpair[0]]
		clust.append(newcluster)
	return clust[0]		


def printclust(clust,labels=None,n=0):
	# отступ для визуализации иерархии
	for i in range(n): print ' ',

	if clust.id < 0:
		# отрицательный id означает, что это внутренний узел
		print '-'
	else:
		# положительный id означает, что это листовый узел
		if labels == None: print clust.id
		else: print labels[clust.id]
	
	# теперь печатаем правую и левую ветви
	if clust.left!=None: printclust(clust.left,labels=labels,n=n+1)
	if clust.right!=None: printclust(clust.right,labels=labels,n=n+1)

################

def getheight(clust):
	# Is this an endpoint? Then the height is just 1
	if clust.left==None and clust.right==None: return 1

	# Otherwise the height is the same of the heights of
	# each branch
	return getheight(clust.left)+getheight(clust.right)

def getdepth(clust):
	# The distance of an endpoint is 0.0
	if clust.left==None and clust.right==None: return 0

	# The distance of a branch is the greater of its two sides
	# plus its own distance
	return max(getdepth(clust.left),getdepth(clust.right))+clust.distance


def drawdendrogram(clust,labels,jpeg='clusters.jpg'):
	# height and width
	h=getheight(clust)*20
	w=1200
	depth=getdepth(clust)

	# width is fixed, so scale distances accordingly
	scaling=float(w-150)/depth

	# Create a new image with a white background
	img=Image.new('RGB',(w,h),(255,255,255))
	draw=ImageDraw.Draw(img)

	draw.line((0,h/2,10,h/2),fill=(255,0,0))    

	# Draw the first node
	drawnode(draw,clust,10,(h/2),scaling,labels)
	img.save(jpeg,'JPEG')


def drawnode(draw,clust,x,y,scaling,labels):
	if clust.id<0:
		h1=getheight(clust.left)*20
		h2=getheight(clust.right)*20
		top=y-(h1+h2)/2
		bottom=y+(h1+h2)/2
		
		# Line length
		ll=clust.distance*scaling
		# Vertical line from this cluster to children    
		draw.line((x,top+h1/2,x,bottom-h2/2),fill=(255,0,0))    
    
		# Horizontal line to left item
		draw.line((x,top+h1/2,x+ll,top+h1/2),fill=(255,0,0))    

		# Horizontal line to right item
		draw.line((x,bottom-h2/2,x+ll,bottom-h2/2),fill=(255,0,0))        

		# Call the function to draw the left and right nodes    
		drawnode(draw,clust.left,x+ll,top+h1/2,scaling,labels)
		drawnode(draw,clust.right,x+ll,bottom-h2/2,scaling,labels)
	else:   
		# If this is an endpoint, draw the item label
		draw.text((x+5,y-7),labels[clust.id],(0,0,0))

####################

# def rotatematrix(data):
#   newdata=[]
#   for i in range(len(data[0])):
#     newrow=[data[j][i] for j in range(len(data))]
#     newdata.append(newrow)
#   return newdata


def kcluster(rows,distance=pearson,k=4):
	# Determine the minimum and maximum values for each point
	ranges=[(min([row[i] for row in rows]),max([row[i] for row in rows])) 
	for i in range(len(rows[0]))]

	# Create k randomly placed centroids
	clusters=[[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] 
	for i in range(len(rows[0]))] for j in range(k)]
  
	lastmatches=None
	for t in range(100):
		print 'Iteration %d' % t
		bestmatches=[[] for i in range(k)]
    
		# Find which centroid is the closest for each row
		for j in range(len(rows)):
			row=rows[j]
			bestmatch=0
			for i in range(k):
				d=distance(clusters[i],row)
				if d<distance(clusters[bestmatch],row): bestmatch=i
			bestmatches[bestmatch].append(j)

		# If the results are the same as last time, this is complete
		if bestmatches==lastmatches: break
		lastmatches=bestmatches
    
		# Move the centroids to the average of their members
		for i in range(k):
			avgs=[0.0]*len(rows[0])
			if len(bestmatches[i])>0:
				for rowid in bestmatches[i]:
					for m in range(len(rows[rowid])):
						avgs[m]+=rows[rowid][m]
				for j in range(len(avgs)):
					avgs[j]/=len(bestmatches[i])
				clusters[i]=avgs
      
	return bestmatches

# def tanamoto(v1,v2):
#   c1,c2,shr=0,0,0
  
#   for i in range(len(v1)):
#     if v1[i]!=0: c1+=1 # in v1
#     if v2[i]!=0: c2+=1 # in v2
#     if v1[i]!=0 and v2[i]!=0: shr+=1 # in both
  
#   return 1.0-(float(shr)/(c1+c2-shr))

def scaledown(data,users,distance=pearson,rate=0.01):
	n=len(data)

	# The real distances between every pair of items
	realdist=[[distance(data[i],data[j]) for j in range(n)] for i in range(0,n)]

	# Randomly initialize the starting points of the locations in 2D
	loc=[[random.random(),random.random()] for i in range(n)]
	fakedist=[[0.0 for j in range(n)] for i in range(n)]
  
	lasterror=None
	for m in range(0,1000):
		# Find projected distances
		for i in range(n):
			for j in range(n):
				fakedist[i][j]=sqrt(sum([pow(loc[i][x]-loc[j][x],2) for x in range(len(loc[i]))]))		
  
		# Move points
		grad=[[0.0,0.0] for i in range(n)]
    
		totalerror=0
		for k in range(n):
			for j in range(n):
				if j==k: continue
				# The error is percent difference between the distances
				if realdist[j][k] > 0:
					errorterm = (fakedist[j][k]-realdist[j][k]) / realdist[j][k]
				else:
					print 'Нулевое расстояние между ', users[j], ' и ', users[k]
					errorterm = 0.5
        
				# Each point needs to be moved away from or towards the other
				# point in proportion to how much error it has
				grad[k][0]+=((loc[k][0]-loc[j][0])/fakedist[j][k])*errorterm
				grad[k][1]+=((loc[k][1]-loc[j][1])/fakedist[j][k])*errorterm

				# Keep track of the total error
				totalerror+=abs(errorterm)
		print totalerror

		# If the answer got worse by moving the points, we are done
		if lasterror and lasterror<totalerror: break
		lasterror=totalerror

		# Move each of the points by the learning rate times the gradient
		for k in range(n):
			loc[k][0]-=rate*grad[k][0]
			loc[k][1]-=rate*grad[k][1]

	return loc

def draw2d(data,labels,jpeg='mds2d.jpg'):
	img=Image.new('RGB',(2000,2000),(255,255,255))
	draw=ImageDraw.Draw(img)
	for i in range(len(data)):
		x=(data[i][0]+0.5)*1000
		y=(data[i][1]+0.5)*1000
		draw.text((x,y),labels[i],(0,0,0))
	img.save(jpeg,'JPEG')  


getwordstats()

users,words,data = readfile('words.txt')

clust = hcluster(data)		
printclust(clust,labels=users)
drawdendrogram(clust,users,jpeg='words.jpg')

# Кластеризация методом К-средних
kclust=kcluster(data,k=5)
print [users[r] for r in kclust[0]]
print [users[r] for r in kclust[1]]
print [users[r] for r in kclust[2]]
print [users[r] for r in kclust[3]]
print [users[r] for r in kclust[4]]
# print [users[r] for r in kclust[5]]
# print [users[r] for r in kclust[6]]
# print [users[r] for r in kclust[7]]
# print [users[r] for r in kclust[8]]
# print [users[r] for r in kclust[9]]

# 2-D визуализация
# users,words,data = readfile('words.txt')
coords=scaledown(data, users)
draw2d(coords,users,jpeg='words2d.jpg')