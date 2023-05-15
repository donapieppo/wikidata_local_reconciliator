#!/usr/bin/env python3

"""
Reads from a wikidata json dumpo and saves in a sqlite3 db. 
"""

import argparse
import json
import bz2
from os.path import exists

from wikidata_local_parser import WikidataLocalParser

parser = argparse.ArgumentParser(description="Parse a wikidata json bz2 dump file "
                                           "and save data in sqlite3 db.")
parser.add_argument('filename', type=str,
                  help='the dump wikipedia file in json.bz2 format.')
parser.add_argument('-db', dest='db', metavar='db', nargs=1, type=str,
                  help='the sqlite3 file to save data.',
                  required=True)

args = parser.parse_args()
filename = args.filename
db = args.db[0]

if (not exists(filename)):
    print(f"No file {filename} to read from.")
    exit(1)

if (not exists(db)):
    print(f"No file {db}. Please prepare the sqlite3 db with"
          "./bin/prepare_db.py -db {db}")
    exit(1)


parser = WikidataLocalParser(db)

with bz2.open(filename, mode='rt') as f:
    if '0000' in filename:
        f.read(2)  # skip first two bytes: "{\n"
    i = 0
    for line in f:
        print(f"{i} {line[0:35]}")
        i += 1
        j = json.loads(line.rstrip(',\n'))
        parser.save(j)

parser.close()

# print(json.dumps(j, indent=2))
