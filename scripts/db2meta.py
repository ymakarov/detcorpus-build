#!/usr/bin/env python
# coding: utf-8

import sqlite3
import argparse
import csv
import re
import html
from collections import defaultdict

class MetaDB(object):
    def __init__(self, dbfile, genres):
        self._conn = sqlite3.connect(dbfile)
        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()
        self._genres = defaultdict(str)
        with open(genres, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                self._genres['/'.join((row[0], row[1]))] = row[2]

    def query(self, query, params=None):
        if params:
            return self._cur.execute(query, params)
        else:
            return self._cur.execute(query)

    def __del__(self):
        self._conn.close()

    def get_all_files(self):
        filelist = []
        for row in self.query('SELECT filename FROM meta_editions WHERE filename IS NOT NULL'):
            filelist.append(row[0])
        return filelist

    def meta_for_file(self, filename):
        metad = {}
        metad['id'] = self.generate_id(filename)
        for row in self.query('SELECT author_name, title, booktitle, year, city, publisher_unified, uuid FROM meta_editions JOIN meta_books ON meta_editions.book_id = meta_books.book_id WHERE filename=?', (filename,)):
            metad.update(row)
        try:
            firstyear = self.get_firstprint(metad['uuid'])
            metad['text_year'] = firstyear
            authors = self.get_authors(metad['uuid'])
            metad.update(authors)
        except (KeyError):
            metad.update(self.fallback_years(filename))
        metad['genre'] = self._genres[filename]
        return metad

    def get_firstprint(self, uuid):
        c = self.query('select MIN(year) from meta_editions JOIN meta_books ON meta_editions.book_id = meta_books.book_id where uuid=?', (uuid,))
        return c.fetchone()[0]

    def get_authors(self, uuid):
        authors = defaultdict(list)
        authorid = self.query('SELECT author_id, pseudo_id FROM text_author WHERE uuid=?', (uuid,))
        for row in authorid:
            if row['pseudo_id']:
                authors['author'].append(self.make_authorname('meta_pseudo', 'pseudo_id', row['pseudo_id']))
                authors['realname'].append(self.make_authorname('meta_authors', 'author_id', row['author_id']))
            else:
                authors['author'].append(self.make_authorname('meta_authors', 'author_id', row['author_id']))
            authordata = self.query('SELECT sex, birth_year, death_year FROM meta_authors WHERE author_id=?', (row['author_id'],)).fetchone()
            authors['author_sex'].append(authordata['sex'])
            authors['author_birth_year'].append(authordata['birth_year'])
            authors['author_death_year'].append(authordata['death_year'])
        return authors

    def make_authorname(self, table, column, a_id):
        c = self.query('SELECT last, first, middle FROM "{}" WHERE {}=?'.format(table.replace('"', '""'), column), (a_id,))
        author = c.fetchone()
        return '{last}, {first} {middle}'.format(**author)

    def generate_id(self, filename):
        m = re.search('[0-9]+s/([^.]+\.[^.]+).*', filename)
        return m.group(1)

    def format_docheader(self, metad):
        values = []
        for k, v in metad.items():
            if isinstance(v, list):
                values.append('{}="{}"'.format(k, html.escape('|'.join([str(i) for i in v]))))
            else:
                values.append('{}="{}"'.format(k, html.escape(str(v))))
        return '<doc {}>'.format(' '.join(values))

    def fallback_years(self, filename):
        out = {}
        m = re.search(u'[^.]+\.[^.]+\.([12][90][0-9][0-9])[._-]([12][90][0-9][0-9])?.*', filename)
        if m:
            year, printed = m.groups()
            out['text_year'] = year
            if printed:
                out['year'] = printed
            else:
                out['year'] = year
        return out
                


def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract metadata from sqlite db')
    parser.add_argument('-d', '--dbfile', help='database file')
    parser.add_argument('-g', '--genres', help='genres.csv file')
    parser.add_argument('-f', '--filename', help='return metadata for a given filename')
    return parser.parse_args()

def main():
    args = parse_arguments()
    if args.filename:
        meta_db = MetaDB(args.dbfile, args.genres)
        metad = meta_db.meta_for_file(args.filename)
        print(meta_db.format_docheader(metad))
        del meta_db

if __name__ == '__main__':
    main()
