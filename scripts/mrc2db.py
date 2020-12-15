#!/usr/bin/env python
# coding: utf-8

import utils
import os
import logging
import re
import argparse

def get_mrc_year(record):
        try:
            year = record['210']['d']
        except TypeError:
            if '100' in record:
                sfs = record['100'].get_subfields('d', 'c')
                if len(sfs) > 0:
                    year = sfs[0]
                else:
                    m = re.search('[^d]+d([12][089][0-9][0-9])', record['100'].value())
                    if m:
                        year = m.group(1)
                    else:
                        year = ''
            else:
                year = ''
        return year

def join_subfields(fieldlist, delimiter=' '):
        out = []
        for sf in fieldlist:
            if not sf:
                continue
            elif isinstance(sf, list):
                sf = '; '.join(sf)
            out.append(sf)
        return delimiter.join(out)

def get_colophon(record):
    yearPart = record['210']
    if yearPart:
        return join_subfields(yearPart.get_subfields('a', 'c', 'd'))
    return None

def get_multi_colophon(filename):
    return get_colophon(utils.get_records(filename)[0])
     
def mrcdata(book_id):
    mrcfile = '../detcorpus/marc/' + str(book_id) + '.mrc'
    if not os.path.isfile(mrcfile):
        logging.warning("Doesn't exist {}".format(mrcfile))
        return None
    records = utils.get_records(mrcfile)
    if len(records) == 0:
        logging.warning('Invalid mrc file {}'.format(mrcfile))
        return None
    record = records[0]
    colophon = None
    if record['461']: # Многотомное издание
        parent_volume = '../detcorpus/marc/_' + str(book_id) + '.mrc'
        if os.path.isfile(parent_volume):
            colophon = get_multi_colophon(parent_volume)
        else:
            logging.exception('No parent volume for {}'.format(book_id))
        sourcetitle = join_subfields(record['461'].get_subfields('a', 'f'), '. ') + ', '
    else:
        sourcetitle = ''
        colophon = get_colophon(record)
    
    titlePart = record['200']
    if titlePart != None: 
        sourcetitle += join_subfields(titlePart.get_subfields('a', 'e', 'f', 'g'), '. ')
    else:
    	logging.exception('No title for book_id {}'.format(book_id))

    year = get_mrc_year(record)
    return (sourcetitle, colophon, year)

def update_not_defined(metadb, book_id, row, pre, data, overwrite = False):
    filename = row['filename']
    (sourcetitle, colophon, year) = data

    if overwrite:
        logging.info("filename: {}, book_id:{}, sourcetitle: {}, colophon: {}, year: {}".format(filename, book_id, sourcetitle, colophon, year))
        metadb.execute("update books set sourcetitle = ?, colophon = ?, year = ? where book_id = ?", (sourcetitle, colophon, year, book_id,))
        return
        
    update = False
    if row[pre + 'sourcetitle'] and row[pre + 'sourcetitle'] != '':
        sourcetitle = row[pre + 'sourcetitle']    
    elif sourcetitle:
        update = True
    if row[pre + 'colophon'] and row[pre + 'colophon'] != '':
        colophon = row[pre + 'colophon']
    elif colophon:
        update = True
    if row[pre + 'year'] and row[pre + 'year'] != 0:
        year = row[pre + 'year']
    elif year: 
        update = True
    if update:
        logging.info("filename: {}, book_id:{}, sourcetitle: {}, colophon: {}, year: {}".format(filename, book_id, sourcetitle, colophon, year))
        metadb.execute("update books set sourcetitle = ?, colophon = ?, year = ? where book_id = ?", (sourcetitle, colophon, year, book_id,))
 
def parse_arguments():
    parser = argparse.ArgumentParser(description='Write data from marc files to db')
    parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrite db data')
    return parser.parse_args()

   

def main(): 
    args = parse_arguments()
    metadb = utils.MetaDb()
    rows = metadb.query("SELECT" 
                " books.book_id,"
                " editions.filename,"
                " books.sourcetitle,"
                " books.colophon,"
                " books.year,"
                " editions.uuid,"
                " first_books.book_id as first_book_id,"
                " first_books.year as first_year,"
                " first_books.sourcetitle as first_sourcetitle,"
                " first_books.colophon as first_colophon"
                " FROM"
                " editions "
                " LEFT JOIN editions as first_editions ON editions.uuid = first_editions.uuid AND first_editions.filename is null"
				" LEFT JOIN books on editions.book_id = books.book_id"
				" LEFT JOIN books as first_books on first_editions.book_id = first_books.book_id"
				" WHERE editions.filename is not null and editions.filename != '' " 
    ).fetchall();
    
    for row in rows:
        book_id = row['book_id']
        data = mrcdata(book_id)
        if data: 
            update_not_defined(metadb, book_id, row, '', data, args.overwrite)
        first_book_id = row['first_book_id']
        if first_book_id:
            data = mrcdata(first_book_id)
            if data:
                update_not_defined(metadb, first_book_id, row, 'first_', data, args.overwrite)
            

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
