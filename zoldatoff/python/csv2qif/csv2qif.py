#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs

decode = 'cp1251'
#decode = 'utf-8'
encode = 'utf-8'

accounts = {'7390': {'name': 'Pocket Bank Green', 'type': 'CCard'},
			'3542': {'name': 'Wage RSB', 'type': 'CCard'},
			'3749': {'name': 'Pocket Bank Gold', 'type': 'CCard'},
			'3709': {'name': 'Transport Card', 'type': 'CCard'}
			}

def ts2date(ts):
	year = ts[0:4]
	month = ts[5:7]
	day = ts[8:10]
	return month + '/' + day + '/' + year

def genattr(instr):
	str = instr.upper()
	ret = {'category': 'Другое', 'contragent': ''}

	if 	 str.find('APPLE') 			>= 0: ret = {'category': 'Онлайн-покупки: Программы', 'contragent': 'Apple'}
	elif str.find('ITUNES')			>= 0: ret = {'category': 'Онлайн-покупки: Программы', 'contragent': 'Apple'}

	elif str.find('MEGAFON')		>= 0: ret = {'category': 'Счета: Сотовая связь', 'contragent': 'Megafon'}
	elif str.find('MTS')			>= 0: ret = {'category': 'Счета: Сотовая связь', 'contragent': 'MTS'}
	elif str.find('BEELINE')		>= 0: ret = {'category': 'Счета: Интернет', 'contragent': 'Beeline'}
	elif str.find('DIPHOST')		>= 0: ret = {'category': 'Счета: Прочее', 'contragent': 'Diphost'}
	elif str.find('MGTS')			>= 0: ret = {'category': 'Счета: Телефон', 'contragent': 'МГТС'}

	elif str.find('READABILITY')	>= 0: ret = {'category': 'Онлайн-покупки: Программы', 'contragent': 'Amazon'}
	elif str.find('AMAZON')			>= 0: ret = {'category': 'Онлайн-покупки: Программы', 'contragent': 'Amazon'}

	elif str.find('PAYPAL')			>= 0: ret = {'category': 'Онлайн-покупки: Paypal', 'contragent': 'Paypal'}

	elif str.find(u'STOLOVAYA')		>= 0: ret = {'category': 'Питание: Столовая', 'contragent': 'Столовая'}
	elif str.find(u'MCDONALDS')		>= 0: ret = {'category': 'Питание: Рестораны', 'contragent': 'Макдоналдс'}
	elif str.find(u'TANUKI')		>= 0: ret = {'category': 'Питание: Рестораны', 'contragent': 'Тануки'}
	elif str.find(u'TEMPL BAR')		>= 0: ret = {'category': 'Питание: Рестораны', 'contragent': 'Темпл-бар'}
	elif str.find(u'KFC')			>= 0: ret = {'category': 'Питание: Рестораны', 'contragent': 'Ростикс'}
	elif str.find(u'STARBUCKS')		>= 0: ret = {'category': 'Питание: Рестораны', 'contragent': 'Старбакс'}
	elif str.find(u'COFFEE HOUSE')	>= 0: ret = {'category': 'Питание: Рестораны', 'contragent': 'Кофе-хаус'}
	elif str.find(u'DVE PALOCHKI')	>= 0: ret = {'category': 'Питание: Рестораны', 'contragent': ''}
	elif str.find(u'SHOKOLADNITSA')	>= 0: ret = {'category': 'Питание: Рестораны', 'contragent': 'Шоколадница'}

	elif str.find(u'PEREKRESTOK')	>= 0: ret = {'category': 'Питание: Продукты', 'contragent': 'Перекресток'}
	elif str.find(u'STANEM DRUZYAMI')	>= 0: ret = {'category': 'Питание: Продукты', 'contragent': 'Станем друзьями'}
	elif str.find(u'SEDMOY KONTINENT')	>= 0: ret = {'category': 'Питание: Продукты', 'contragent': 'Седьмой континент'}
	elif str.find(u'KVARTAL')		>= 0: ret = {'category': 'Питание: Продукты', 'contragent': 'Квартал'}
	elif str.find(u'MAGNOLIYA')		>= 0: ret = {'category': 'Питание: Продукты', 'contragent': 'Магнолия'}

	elif str.find(u'OLLGUD')		>= 0: ret = {'category': 'Питание: Прочее', 'contragent': ''}
	elif str.find(u'AROMATNYI MIR')	>= 0: ret = {'category': 'Питание: Прочее', 'contragent': ''}

	elif str.find(u'BELYY VETER')	>= 0: ret = {'category': 'Техника', 'contragent': 'Белый ветер'}

	elif str.find(u'GUINOT')		>= 0: ret = {'category': 'Услуги', 'contragent': 'Guinot'}

	elif str.find(u'KOSMIK')		>= 0: ret = {'category': 'Досуг: Развлечения', 'contragent': 'Космик'}

	elif str.find(u'APTEKA')		>= 0: ret = {'category': 'Здоровье: Аптека', 'contragent': 'Аптека'}
	elif str.find(u'STARYY LEKAR')	>= 0: ret = {'category': 'Здоровье: Аптека', 'contragent': 'Аптека'}
	elif str.find(u'LINZMASTER')	>= 0: ret = {'category': 'Здоровье: Линзы', 'contragent': ''}

	elif str.find(u'RZD')			>= 0: ret = {'category': 'Путешествия', 'contragent': 'РЖД'}
	elif str.find(u'МЕТРОПОЛИТЕН')	>= 0: ret = {'category': 'Транспорт', 'contragent': 'Метро'}

	elif str.find(u'ATM')			>= 0: ret = {'category': 'Cash', 'contragent': 'Zoldatoff'}

	elif str.find(u'ПЕРЕВОД')		>= 0: ret = {'category': 'Перевод', 'contragent': 'Zoldatoff'}
	elif str.find(u'КОМИССИ')		>= 0: ret = {'category': 'Банк: Комиссии и штрафы', 'contragent': 'RSB'}
	elif str.find(u'COMISSION')		>= 0: ret = {'category': 'Банк: Комиссии и штрафы', 'contragent': 'RSB'}
	elif str.find(u'ПРОЦЕНТ')		>= 0: ret = {'category': 'Инвестиции', 'contragent': 'RSB'}

	elif str.find(u'З/ПЛАТЫ')		>= 0: ret = {'category': 'Зарплата', 'contragent': 'RSB'}
	elif str.find(u'АВАНС')			>= 0: ret = {'category': 'Зарплата', 'contragent': 'RSB'}

	elif str.find(u'МАТЕРИАЛЬНАЯ')	>= 0: ret = {'category': 'Другое', 'contragent': ''}

	#ret.setdefault('type', 'Bank')

	return {k: unicode(v, encode) for k,v in ret.items()}

def gentrans(colnames, values):
	trans = dict(zip(colnames, values))

	# incoming or outcoming transaction
	if trans.pop('type') == '0': trans['amount'] = '-' + trans['amount']

	#date format
	trans['date'] = ts2date(trans.pop('timestamp'))

	# add category and contragent
	a = genattr(trans['description'])
	trans.update(a)

	return trans

def writeacc(accnum, outfile, translist=1):
	acc = accounts[accnum]

	data = ''
	if translist == 1: data += '!Account\n'
	data += 'N' + acc['name'] + '\n'
	data += 'T' + acc['type'] + '\n'
	data += '^\n'
	if translist == 1: data += '!Type:Bank\n'

	outfile.write(data)

def writetrans(trans, outfile):
	data = ''
	#data = '!Type:' + trans['type'] + '\n'
	data += 'D' + trans['date'] + '\n'	
	data += 'T' + trans['amount'] + '\n'
	data += 'M' + trans['description'] + '\n'
	data += 'L' + trans['category'] + '\n'	# L[target account]
	data += 'P' + trans['contragent'] + '\n'
	data += '^\n'

	outfile.write(data)

def csv2qif(filename):
	infile = codecs.open(filename, 'r', decode)
	outfile = codecs.open('output.qif','a+',encode)

	# Write all accounts data
	#outfile.write('!Account\n')
	#for accnum in accounts.keys():
	#	writeacc(accnum, outfile, 0)	

	# Read transactions
	data = infile.readlines()
	lines = [line for line in data]
	colnames = lines[0].strip( ).split(',')
	accnum = lines[1][2:6]

	# Начинаем писать транзакции для нового счета
	#writeacc(accnum, outfile)
	for line in lines[1:]:
		values = line.strip( ).split(',')
		trans = gentrans(colnames, values)
		writetrans(trans, outfile)

outfile = codecs.open('output.qif','w',encode)
writeacc('3709', outfile)
csv2qif('./cvs/tr/02.csv')
csv2qif('./cvs/tr/03.csv')
csv2qif('./cvs/tr/04.csv')