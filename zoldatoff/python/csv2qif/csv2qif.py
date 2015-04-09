#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs

DECODE_FILTER = 'utf-8'
DECODE_CSV = 'cp1251'
ENCODE_QIF = 'utf-8'
DEBUG = 0

accounts = {'7390': {'name': u'БвК Green', 'type': 'CCard'},
            '3542': {'name': u'Зарплатка', 'type': 'CCard'},
            '9092': {'name': u'Женька Travel', 'type': 'CCard'},
            '3749': {'name': u'БвК Gold', 'type': 'CCard'},
            '3763': {'name': u'Travel', 'type': 'CCard'},
            '3709': {'name': u'Transport', 'type': 'CCard'}}


def csv2qif(infile, outfile, filter_data):
    """
    Читает данные транзакций из csv-файла и вызывает создание qif-файла
    """
    infile = codecs.open(infile, 'r', DECODE_CSV)

    if DEBUG >= 1:
        print '...Reading transactions from file...'
    data = infile.readlines()
    lines = [line for line in data if line.strip()]
    colnames = lines[0].strip().split(',')
    accnum = lines[1][2:6]

    if DEBUG >= 1:
        print '...Writing qif header...'
    writeacc(accnum, outfile)

    if DEBUG >= 1:
        print '...Parsing transactions...'
    for line in lines[1:]:
        values = line.strip().split(',')
        trans = gentrans(colnames, values, filter_data)
        writetrans(trans, outfile)


def writeacc(accnum, outfile, translist=1):
    """
    Пишет заголовок qif-файла с данными о счёте
    """
    if DEBUG >= 2:
        print '......accnum =', accnum

    acc = accounts[accnum]

    if DEBUG >= 0:
        print 'Account name:', acc['name']

    data = ''
    if translist == 1:
        data += '!Account\n'
    data += 'N' + acc['name'] + '\n'
    data += 'T' + acc['type'] + '\n'
    data += '^\n'
    if translist == 1:
        data += '!Type:Bank\n'

    outfile.write(data)


def gentrans(colnames, values, filter_data):
    """
    Преобразует строку csv-файла в список
    """
    if DEBUG >= 2:
        '......Converting csv data to qif data......'

    trans = dict(zip(colnames, values))

    # incoming or outcoming transaction
    if trans.pop('type') == '0':
        trans['amount'] = '-' + trans['amount']

    # date format
    trans['date'] = ts2date(trans.pop('timestamp'))

    # add category and contragent
    a = classify_transaction(
        trans['description'], trans['amount'][0], filter_data)
    trans.update(a)

    return trans


def writetrans(trans, outfile):
    """
    Записывает в файл данные одной транзакции
    """
    if DEBUG >= 2:
        print '......Writing transaction to file...'
        print '         Date =', trans['date']
        print '         Amount =', trans['amount']
        print '         Description =', trans['description']
        print '         Category =', trans['category']
        print '         Contragent =', trans['contragent']

    data = ''
    # data = '!Type:' + trans['type'] + '\n'
    data += 'D' + trans['date'] + '\n'
    data += 'T' + trans['amount'] + '\n'
    data += 'M' + trans['description'] + '\n'
    data += 'L' + trans['category'] + '\n'  # L[target account]
    data += 'P' + trans['contragent'] + '\n'
    data += '^\n'

    outfile.write(data)


def classify_transaction(transaction_name, transaction_sign, filter_data):
    """
    Классифицирует транзакции, сопоставляя ключевые слова с фильтром
    """
    if DEBUG >= 2:
        print '......Classification: ', transaction_name

    tr_name_upper = transaction_name.upper()

    if tr_name_upper.find(u'ПЕРЕВОД') >= 0 and transaction_sign == '-':
        return {'category': u'Перевод (-)', 'contragent': ''}

    lines = [line for line in filter_data if line.strip() and line[0] != '#']
    for line in lines:
        values = line.strip().split('\t')
        if len(values) < 2:
            print '!!! Check filter file:', values
            values.extend([u'Другое', ''])
        elif len(values) < 3:
            if DEBUG > 2:
                print '........Generating null contragent:', values
            values.append('')
        if tr_name_upper.find(values[0].upper()) >= 0:
            result = {'category': values[1], 'contragent': values[2]}
            if DEBUG >= 2:
                print '......Classification succeeded:', \
                      'category =', values[1], \
                      ', contragent =', values[2]
            return result

    if DEBUG >= 0:
        print '!Cannot classify:', transaction_name
    return {'category': u'Другое', 'contragent': ''}


def ts2date(ts):
    """
    Преобразует timestamp в дату
    """
    year = ts[0:4]
    month = ts[5:7]
    day = ts[8:10]
    return month + '/' + day + '/' + year

#####################################################
#####################################################

filter_file = codecs.open('filters.txt', 'r', DECODE_FILTER)
filter_data = filter_file.readlines()

if sys.argv[1]:
    CSV_PATH = './' + sys.argv[1] + '/'
else:
    CSV_PATH = './201503/'

files = [os.path.splitext(f)[0]
         for f in os.listdir(CSV_PATH)
         if os.path.splitext(f)[1] == '.csv']

for file_name in files:
    print '*************************************************'
    print 'File name:', file_name
    if os.path.exists(file_name + '.qif'):
        print 'File already exists:', file_name + '.qif'
    else:
        outfile = codecs.open(CSV_PATH + file_name + '.qif', 'w', ENCODE_QIF)
        csv2qif(CSV_PATH + file_name + '.csv', outfile, filter_data)
        outfile.close()
