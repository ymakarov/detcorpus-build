#!/usr/bin/env python3
# coding: utf-8


import re
import sys
import argparse
from collections import defaultdict


def parse_arguments():
    parser = argparse.ArgumentParser(description='Implant data on LDA topics into a .vert file')
    parser.add_argument('-l', '--labels', nargs='+',
                        help="Labels to use as metadata attributes")
    parser.add_argument('-t', '--topics', nargs='+',
                        help="Labels for the topics")
    parser.add_argument('-d', '--doctopics', nargs='+',
                        help="Doc-topics table data from mallet")
    parser.add_argument('-i', '--infile',
                        help=".vert file to be processed")
    parser.add_argument('-o', '--outfile',
                        help="Output file")
    return parser.parse_args()


def get_id(line):
    """extract id value from a .vert line with metadata"""
    m = re.search('^<.* id="?([^" >]+)"?', line)
    if m:
        return m.group(1)
    else:
        return None


def print_topics(docid, fragid, labels, fragtopics):
    """prepare attribute string listing all topics known for a fragment"""
    out = []
    for lbl in labels:
        mdl = []
        try:
            ftopics = fragtopics[lbl][(docid, fragid)]
        except KeyError:
            ftopics = []
            sys.stderr.write('WARNING: no topics found for the fragment: {} {}\n'.format(docid, fragid))
        for orig in ftopics:
            mdl.append('_'.join(labels[lbl][orig]))
        out.append('{0}="{1}"'.format(lbl, '|'.join(mdl)))
    return ' '.join(out)


def main():
    args = parse_arguments()
    labels = defaultdict(dict)
    fragtopics = defaultdict(dict)
    for lbl, tpc, dt in zip(args.labels, args.topics, args.doctopics):
        with open(tpc, 'r') as ls:
            for line in ls:
                size, orig, label = line.strip().split()
                labels[lbl][orig] = (size, label)
        with open(dt, 'r') as dts:
            for line in dts:
                if line.startswith('#'):
                    continue
                fields = line.strip().split('\t')
                fragtopics[lbl][(fields[1], fields[2])] = fields[3::2]
    with open(args.infile, 'r') as infile:
        with open(args.outfile, 'w') as outfile:
            for line in infile:
                if line.startswith("<doc"):
                    docid = get_id(line)
                    outfile.write(line)
                elif line.startswith("<f"):
                    fragid = get_id(line)
                    lda = print_topics(docid, fragid, labels, fragtopics)
                    outfile.write("<f id={0} {1}>\n".format(fragid, lda))
                else:
                    outfile.write(line)

if __name__ == '__main__':
    main()
