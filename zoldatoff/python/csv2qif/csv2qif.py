#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs

decode = 'cp1251'
#decode = 'utf-8'
encode = 'utf-8'

def ts2date(ts):
	year = ts[0:4]
	month = ts[5:7]
	day = ts[8:10]
	return month + '/' + day + '/' + year

def category(instr):
	str = instr.upper()
	ret = ''

	if str.find('APPLE') 	>= 0: ret = 'Онлайн-покупки: Программы'
	if str.find('ITUNES')	>= 0: ret = 'Онлайн-покупки: Программы'

	if str.find('MEGAFON')	>= 0: ret = 'Счета: Сотовая связь'
	if str.find('MTS')		>= 0: ret = 'Счета: Сотовая связь'
	if str.find('BEELINE')	>= 0: ret = 'Счета: Интернет'
	if str.find('DIPHOST')	>= 0: ret = 'Счета: Другое'

	if str.find('READABILITY')	>= 0: ret = 'Онлайн-покупки: Программы'
	if str.find('AMAZON')	>= 0: ret = 'Онлайн-покупки: Программы'

	if str.find('PAYPAL')	>= 0: ret = 'Онлайн-покупки: Paypal'

	if str.find(u'ПЕРЕВОД')	>= 0: ret = 'Банк: Перевод'
	if str.find(u'КОМИССИ')	>= 0: ret = 'Банк: Комиссии и штрафы'
	if str.find(u'ПРОЦЕНТ')	>= 0: ret = 'Банк: Проценты'

	return unicode(ret, encode)

def contragent(instr):
	str = instr.upper()
	ret = ''

	if str.find('APPLE') 	>= 0: ret = 'Apple'
	if str.find('ITUNES')	>= 0: ret = 'Apple'

	if str.find('MEGAFON')	>= 0: ret = 'Megafon'
	if str.find('MTS')		>= 0: ret = 'MTS'
	if str.find('BEELINE')	>= 0: ret = 'Beeline'
	if str.find('DIPHOST')	>= 0: ret = 'Diphost'

	if str.find('READABILITY')	>= 0: ret = 'Amazon'
	if str.find('AMAZON')	>= 0: ret = 'Amazon'

	if str.find('PAYPAL')	>= 0: ret = 'Paypal'

	if str.find(u'ПЕРЕВОД')	>= 0: ret = 'Zoldatoff'
	if str.find(u'КОМИССИ')	>= 0: ret = 'RSB'
	if str.find(u'ПРОЦЕНТ')	>= 0: ret = 'RSB'

	return unicode(ret, encode)


def readfile(filename):
	infile = codecs.open(filename, 'r', decode)
	outfile = codecs.open('output.qif','w',encode)

	data = infile.readlines()
	lines=[line for line in data]
	# Первая строка содержит названия столбцов
	colnames=lines[0].strip( ).split(',')[0:]

	n = len(colnames)

	print [colnames[r] for r in range(n)]

	outfile.write('!Account\n')
	outfile.write('NTest\n')
	outfile.write('TCCard\n')
	outfile.write('^\n')

	outfile.write('!Type:CCard\n')
	for line in lines[1:]:
		p = line.strip( ).split(',')
		for r in range(len(p)):
			if colnames[r] == 'type' and p[r]=='0': sign = '-'
			if colnames[r] == 'type' and p[r]=='1': sign = ''

			if colnames[r] == 'timestamp': outfile.write('D' + ts2date(p[r]) + '\n')	#date
			if colnames[r] == 'amount': outfile.write('T' + sign + p[r] + '\n')			#amount

			if colnames[r] == 'description': outfile.write('M' + p[r] + '\n')			#memo
			if colnames[r] == 'description': outfile.write('L' + category(p[r]) + '\n')	#category
			if colnames[r] == 'description': outfile.write('P' + contragent(p[r]) + '\n')	#contragent
		outfile.write('^\n')

		print [p[r] for r in range(len(p))]

#readfile('pocketbank.csv')
readfile('report.csv')