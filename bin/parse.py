#!/usr/bin/env python3

"""
Reads from a wikidata json dumpo and saves in a sqlite3 db. 
"""

import argparse
import json
import bz2
from os.path import exists

from wikidata_local_parser import WikidataLocalParser

args = argparse.ArgumentParser(description="Parse a wikidata gz dump file "
                                           "and save in sqlite3 db.")
args.add_argument('-f', dest='filename', metavar='filename', nargs=1, type=str,
                  help='the dump wikipedia file in gz format.',
                  required=True)
args.add_argument('-db', dest='db', metavar='filename', nargs=1, type=str,
                  help='the sqlite3 file to save data.',
                  required=True)

args = args.parse_args()
filename = args.filename[0]
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
