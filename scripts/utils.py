#!/usr/bin/env python
# coding: utf-8

# Утилиты для работы с marc файлами
# - Reload python module
# from importlib import reload
# reload(module)

import os
import sqlite3

from typing import List
from pymarc import MARCReader
from shutil import copyfile
from urllib import request

def get_records(filename: str) -> List:
    records = []
    with open(filename, 'rb') as fh:
        reader = MARCReader(fh, to_unicode=True, force_utf8=True)
        for record in reader:
            records.append(record)
    return records   



def read_mrc_files():
    return {file: get_records('../detcorpus/marc/' + file) for file in os.listdir('../detcorpus/marc')}


def find_parents(fileRecords = read_mrc_files()):
    index = {fileRecords[key][0]['001'].data: key for key in fileRecords if len(fileRecords[key]) > 0}
    tocopy = [(file, index[records[0]['461']['1'][3:]]) 
                for (file, records) in fileRecords.items() 
                if len(records) > 0 and records[0]['461'] and 
                    not '_' + file in fileRecords and records[0]['461']['1'][3:] in index]
    return tocopy

def copy_parents(parents):
   for (child, parent) in parents:
        print("copy {} to {}".format(parent, "_" + child)) 
        copyfile("mrc/" + parent, "mrc/_" + child) 

def read_notes():
    with open('list.txt') as f:
        return f.read()

def find_absent_duplicates(fileRecords = read_mrc_files()):
    notFound = {file for (file, records) in fileRecords.items() if len(records) > 0 and '461' in records[0] and not (('_' + file) in fileRecords)}
    x = read_notes()
    ok = {x.split(', ')[0]: x.split(', ')[1] for x in x.split('\n') if x.find('d') > 0 or x.find('j') > 0 or x.find('-') > 0}
    absent_duplicates = [x for x in notFound if x in ok and ok[x] == 'd']
    absent_duplicates.sort()
    return absent_duplicates

class MetaDb:

    def __init__(self):
        self._conn = sqlite3.connect("meta.db")
        self._conn.row_factory = sqlite3.Row

    def __del__(self):
        self._conn.close()

    def query(self, sql, params = None):
        if params:
            return self._conn.execute(sql, params)
        else:
            return self._conn.execute(sql)

    def execute(self, sql, params = None):
        if params:
            self._conn.execute(sql, params)
        else:
            self._conn.execute(sql)
        self._conn.commit()
 

 
def find_absent_mrc(metadb):
    rows = metadb.query("select book_id, download_link from books where download_link is not null and download_link <> ''").fetchall()
    files = {f for f in os.listdir('../detcorpus/marc')}
    return [r for r in rows if str(r[0]) + '.mrc' not in files]

def download_absent(rows):
    for r in rows:
        save_url_to_file(r[2], '../detcorpus/marc/' + str(r[0]) + '.mrc')

def save_url_to_file(url, filename):
    print('Save {} to {}'.format(url, filename))
    response = request.urlopen(url)
    with open(filename, 'w') as f:
        for line in response:
            f.write(line.decode('utf-8'))
