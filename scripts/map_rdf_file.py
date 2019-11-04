
from __future__ import print_function

import argparse
import gc
import json
import sys
import time

from collections import defaultdict
from io import BytesIO
from os.path import isdir, isfile, join
from rdflib.plugins.parsers.ntriples import NTriplesParser, ParseError, Sink

from bdb_tool import BdbRDFGraph


def parse_args():
    desc = 'Read RDF file and create a set of Berkeley DB files to describe it, ' \
           'to enable querying it in a memory-constrained environment.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('inpath', help='path to input file')
    parser.add_argument('outpath', help='path to output dir')
    return parser.parse_args()


class ElementStrError(Exception):
    pass


def element_str(element):
    ''' Return string representation for rdf element. '''
    try:
        return str(element).encode('unicode_escape')
    except UnicodeEncodeError:
        try:
            return element.toPython().encode('unicode_escape')
        except Exception as e:
            print(e.__class__.__name__, ':', e.args[0])
            print('type(element) =', type(element))
            raise ElementStrError()


class BdbSink(Sink, BdbRDFGraph):
    def __init__(self, outpath):
        self.nlines = 0
        BdbRDFGraph.__init__(self, outpath)
        self.progress_time = self.last_gc_time = time.time()

    def progress(self, count):
        now = time.time()
        if now < self.progress_time + 0.1:
            return
        self.progress_time = now
        sys.stderr.write('progress: {}    \r'.format(count))

    def map_edge(self, db, sid, pid, oid):
        s_edges = set([tuple(edge) for edge in json.loads(db.get(sid) or '[]')])
        s_edge = (pid.decode('ascii'), oid.decode('ascii'))
        if s_edge not in s_edges:
            s_edges.add(s_edge)
            db[sid] = json.dumps(list(s_edges))

    def triple(self, s, p, o):
        self.nlines += 1
        sid = self.nouns.element_id(element_str(s))
        pid = self.verbs.element_id(element_str(p))
        oid = self.nouns.element_id(element_str(o))
        self.map_edge(self.in_edges, oid, pid, sid)
        self.map_edge(self.out_edges, sid, pid, oid)

        now = time.time()
        if now - self.last_gc_time > 100:
            print('gc', now)
            gc.collect()
            self.last_gc_time = now

        self.progress(self.nlines)


def process_file(infile, sink):
    bad_lines = defaultdict(int)
    for line in infile:
        s = BytesIO()
        s.write(line)
        s.seek(0)
        parser = NTriplesParser(sink)
        try:
            parser.parse(s)
        except (ParseError, ElementStrError) as e:
            bad_lines[line] += 1

    print('read {} lines from {}'.format(sink.nlines, infile.name))
    print('bad lines and their frequencies:')
    for line, count in bad_lines.items():
        print('  {:>10} : {}'.format(count, line))


def main():
    args = parse_args()
    if not isfile(args.inpath):
        sys.exit('E: no such file {}'.format(args.inpath))
    if not isdir(args.outpath):
        sys.exit('E: no such dir {}'.format(args.outpath))
    process_file(open(args.inpath, 'rb'), BdbSink(args.outpath))


if __name__ == '__main__':
    main()
