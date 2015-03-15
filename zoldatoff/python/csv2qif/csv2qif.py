#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs

decode = 'cp1251'
# decode = 'utf-8'
encode = 'utf-8'

accounts = {'7390': {'name': u'БвК Green', 'type': 'CCard'},
            '3542': {'name': u'Зарплатка', 'type': 'CCard'},
            '3749': {'name': u'БвК Gold', 'type': 'CCard'},
            '3763': {'name': u'Travel', 'type': 'CCard'},
            '3709': {'name': u'Transport', 'type': 'CCard'}}


def ts2date(ts):
    year = ts[0:4]
    month = ts[5:7]
    day = ts[8:10]
    return month + '/' + day + '/' + year


def genattr(instr, amount_sign):
    str = instr.upper()
    ret = {'category': 'Другое', 'contragent': ''}

    if str.find(u'APPLE') >= 0:
        ret = {'category': 'Электроника: Другое', 'contragent': 'Apple'}
    elif str.find('ITUNES') >= 0:
        ret = {'category': 'Электроника: Музыка', 'contragent': 'Apple'}
    elif str.find(u'OZON') >= 0:
        ret = {'category': 'Электроника', 'contragent': 'Озон'}

    elif str.find('MEGAFON') >= 0:
        ret = {'category': 'Счета: Сотовая связь', 'contragent': 'Megafon'}
    elif str.find('MTS') >= 0:
        ret = {'category': 'Счета: Сотовая связь', 'contragent': 'MTS'}
    elif str.find('BEELINE') >= 0:
        ret = {'category': 'Счета: Интернет', 'contragent': 'Beeline'}
    elif str.find('DIGITALOCEAN.COM') >= 0:
        ret = {'category': 'Счета: Другое', 'contragent': 'Digitalocean'}
    elif str.find('MGTS') >= 0:
        ret = {'category': 'Счета: Телефон', 'contragent': 'МГТС'}

    elif str.find('AMAZON') >= 0:
        ret = {'category': 'Электроника: Другое', 'contragent': 'Amazon'}
    elif str.find('PAYPAL') >= 0:
        ret = {'category': 'Электроника: Другое', 'contragent': 'Paypal'}

    elif str.find(u'MCDONALDS') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Макдоналдс'}
    elif str.find(u'TANUKI') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Тануки'}
    elif str.find(u'TEMPL BAR') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Темпл-бар'}
    elif str.find(u'TORRO GRILL') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Торро-гриль'}
    elif str.find(u'KFC') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Ростикс'}
    elif str.find(u'STARBUCKS') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Старбакс'}
    elif str.find(u'COFFEE HOUSE') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Кофе-хаус'}
    elif str.find(u'DVE PALOCHKI') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': ''}
    elif str.find(u'SHOKOLADNITSA') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Шоколадница'}
    elif str.find(u'GALEREYA ALEKS') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Шоколадница'}
    elif str.find(u'TERRITORIYA') >= 0:
        ret = {'category': 'Питание: Питание вне дома', 'contragent': 'Территория'}

    elif str.find(u'BILLA') >= 0:
        ret = {'category': 'Питание: Бакалея', 'contragent': 'Билла'}
    elif str.find(u'AUCHAN') >= 0:
        ret = {'category': 'Питание: Бакалея', 'contragent': 'Ашан'}
    elif str.find(u'PEREKRESTOK') >= 0:
        ret = {'category': 'Питание: Бакалея', 'contragent': 'Перекресток'}
    elif str.find(u'STANEM DRUZYAMI') >= 0:
        ret = {'category': 'Питание: Бакалея', 'contragent': 'Станем друзьями'}
    elif str.find(u'SEDMOY KONTINENT') >= 0:
        ret = {'category': 'Питание: Бакалея', 'contragent': 'Седьмой континент'}
    elif str.find(u'KVARTAL') >= 0:
        ret = {'category': 'Питание: Бакалея', 'contragent': 'Квартал'}
    elif str.find(u'MAGNOLIYA') >= 0:
        ret = {'category': 'Питание: Бакалея', 'contragent': 'Магнолия'}
    elif str.find(u'SHOP.AV.RU') >= 0:
        ret = {'category': 'Питание: Бакалея', 'contragent': 'Азбука вкуса'}
    elif str.find(u'AROMATNYI MIR') >= 0:
        ret = {'category': 'Питание: Бакалея', 'contragent': 'Ароматный мир'}

    elif str.find(u'ROSNEFT') >= 0:
        ret = {'category': 'Автомобиль: Топливо', 'contragent': ''}

    elif str.find(u'KOSMIK') >= 0:
        ret = {'category': 'Досуг: Развлечения', 'contragent': 'Космик'}
    elif str.find(u'EVROPARTNER') >= 0:
        ret = {'category': 'Досуг: Развлечения', 'contragent': 'Черепаха'}
    elif str.find(u'RHYTHM AND BLUES') >= 0:
        ret = {'category': 'Досуг: Развлечения', 'contragent': 'Дом у дороги'}
    elif str.find(u'FORMULA KINO') >= 0:
        ret = {'category': 'Досуг: Развлечения', 'contragent': 'Кинотеатр'}
    elif str.find(u'KF OCTOBER CINEMA') >= 0:
        ret = {'category': 'Досуг: Развлечения', 'contragent': 'Кинотеатр'}
    elif str.find(u'KASSA.RAMBLER') >= 0:
        ret = {'category': 'Досуг: Развлечения', 'contragent': 'Кинотеатр'}
    elif str.find(u'STAFF STUDIO') >= 0:
        ret = {'category': 'Досуг:Забота о себе', 'contragent': 'Парикмахерская'}

    elif str.find(u'HAWES & CURTIS') >= 0:
        ret = {'category': 'Одежда и обувь: Одежда', 'contragent': 'Hawes & Curtis'}
    elif str.find(u'KHIMCHISTKA') >= 0:
        ret = {'category': 'Одежда и обувь:Другое', 'contragent': 'Химчистка'}

    elif str.find(u'APTEKA') >= 0:
        ret = {'category': 'Здоровье: Аптека', 'contragent': 'Аптека'}
    elif str.find(u'STARYY LEKAR') >= 0:
        ret = {'category': 'Здоровье: Аптека', 'contragent': 'Аптека'}
    elif str.find(u'LINZMASTER') >= 0:
        ret = {'category': 'Здоровье: Уход за глазами', 'contragent': ''}

    elif str.find(u'RZD') >= 0:
        ret = {'category': 'Путешествия', 'contragent': 'РЖД'}
    elif str.find(u'МЕТРОПОЛИТЕН') >= 0:
        ret = {'category': 'Транспорт', 'contragent': 'Метро'}

    elif str.find(u'ATM') >= 0:
        ret = {'category': 'Перевод (-)', 'contragent': 'Zoldatoff'}
    elif str.find(u'Снято наличными') >= 0:
        ret = {'category': 'Перевод (-)', 'contragent': 'Zoldatoff'}
    elif str.find(u'ПЕРЕВОД') >= 0 and amount_sign == '-':
        ret = {'category': 'Перевод (-)', 'contragent': ''}
    elif str.find(u'ПЕРЕВОД') >= 0:
        ret = {'category': 'Перевод (+)', 'contragent': ''}
    elif str.find(u'КОМИССИ') >= 0:
        ret = {'category': 'Сборы', 'contragent': 'RSB'}
    elif str.find(u'COMISSION') >= 0:
        ret = {'category': 'Сборы', 'contragent': 'RSB'}
    elif str.find(u'НАЧИСЛЕНИЕ ПРОЦЕНТОВ') >= 0:
        ret = {'category': 'Инвестиции', 'contragent': 'RSB'}
    elif str.find(u'ПРОЦЕНТЫ') >= 0:
        ret = {'category': 'Ссуды', 'contragent': 'RSB'}

    elif str.find(u'З/ПЛАТЫ') >= 0:
        ret = {'category': 'Зарплата', 'contragent': 'RSB'}
    elif str.find(u'АВАНС') >= 0:
        ret = {'category': 'Зарплата', 'contragent': 'RSB'}

    elif str.find(u'МАТЕРИАЛЬНАЯ') >= 0:
        ret = {'category': 'Другое', 'contragent': ''}

    # ret.setdefault('type', 'Bank')

    return {k: unicode(v, encode) for k, v in ret.items()}


def gentrans(colnames, values):
    trans = dict(zip(colnames, values))

    # incoming or outcoming transaction
    if trans.pop('type') == '0':
        trans['amount'] = '-' + trans['amount']

    # date format
    trans['date'] = ts2date(trans.pop('timestamp'))

    # add category and contragent
    a = genattr(trans['description'], trans['amount'][0])
    trans.update(a)

    return trans


def writeacc(accnum, outfile, translist=1):
    acc = accounts[accnum]

    data = ''
    if translist == 1:
        data += '!Account\n'
    data += 'N' + acc['name'] + '\n'
    data += 'T' + acc['type'] + '\n'
    data += '^\n'
    if translist == 1:
        data += '!Type:Bank\n'

    outfile.write(data)


def writetrans(trans, outfile):
    data = ''
    # data = '!Type:' + trans['type'] + '\n'
    data += 'D' + trans['date'] + '\n'
    data += 'T' + trans['amount'] + '\n'
    data += 'M' + trans['description'] + '\n'
    data += 'L' + trans['category'] + '\n'  # L[target account]
    data += 'P' + trans['contragent'] + '\n'
    data += '^\n'

    outfile.write(data)


def csv2qif(infile, outfile):
    infile = codecs.open(infile, 'r', decode)
    # outfile = codecs.open('output.qif', 'a+', encode)

    # Write all accounts data
    # outfile.write('!Account\n')
    # for accnum in accounts.keys():
    #   writeacc(accnum, outfile, 0)

    # Read transactions
    data = infile.readlines()
    lines = [line for line in data]
    colnames = lines[0].strip().split(',')
    accnum = lines[1][2:6]

    writeacc(accnum, outfile)

    # Начинаем писать транзакции для нового счета
    # writeacc(accnum, outfile)
    for line in lines[1:]:
        values = line.strip().split(',')
        trans = gentrans(colnames, values)
        writetrans(trans, outfile)


CSV_PATH = './201502/'
files = [os.path.splitext(f)[0]
         for f in os.listdir(CSV_PATH)
         if os.path.splitext(f)[1] == '.csv']

for file_name in files:
    outfile = codecs.open(CSV_PATH + file_name + '.qif', 'w', encode)
    csv2qif(CSV_PATH + file_name + '.csv', outfile)
    outfile.close()
