#!/usr/bin/env python3
# coding: utf-8

import sys
import re
import xml.etree.cElementTree as e
from collections import defaultdict


def parse_grammemes(attr):
    const, variable = attr.split(u'=')
    tags = const.split(u',')
    pos = tags[0]
    constgram = u'|'.join(tags[1:])
    vargram = variable.strip('()')
    d = {'tag': pos,
         'const': constgram,
         'var': vargram}
    return d


def print_token(fields):
    s = u'{f[word]}\t{f[lemma]}\t{f[tag]}\t{f[const]}\t{f[var]}\n'.format(f=fields)
    sys.stdout.write(s)


def print_header(filename):
    m = re.search(u'([a-zA-Z_]+\.[0-9a-zA-Z._-]+[a-zA-Z]?[0-9]?)\.([12][90][0-9][0-9])[._]([12][90][0-9][0-9])?.*', filename)
    if m:
        id, year, printed = m.groups()
        if not printed:
            printed = 'UNDEF'
        h = u'<doc id="{0}" text_year="{1}" source_year="{2}">\n<f id=1>\n<s>\n'.format(id, year, printed)
    else:
        h = u'<doc>\n<f id=1>\n<s>\n'
    sys.stdout.write(h)


def print_footer():
    sys.stdout.write(u"</s>\n</f>\n</doc>\n")


def main():
    fragsize = 500
    itoken = 0
    fragid = 1
    print_header(sys.argv[1])
    fields = defaultdict(str)
    for event, elem in e.iterparse(sys.stdin):
        if elem.tag == 'se':
            sys.stdout.write("</s>\n<s>\n")
        elif elem.tag == 'ana':
            fields['lemma'] = elem.get('lex')
            gr = parse_grammemes(elem.get('gr'))
            fields.update(gr)
        elif elem.tag == 'w':
            fields['word'] = u''.join(elem.itertext())
            print_token(fields)
            itoken += 1
            if (itoken % fragsize) == 0:
                fragid += 1
                sys.stdout.write("</f>\n<f id={}>\n".format(fragid))
            fields = defaultdict(str)
            try:
                tail = elem.tail.strip()
            except AttributeError:
                tail = None
            if tail:
                print_token(defaultdict(str, word=tail, tag='c', lemma=tail))
                itoken += 1
                if (itoken % fragsize) == 0:
                    fragid += 1
                    sys.stdout.write("</f>\n<f id={}>\n".format(fragid))
    print_footer()


if __name__ == '__main__':
    main()



    
