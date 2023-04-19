#!/usr/bin/env python3

"""
Just a simple search interface to test. 
"""

import argparse
import sqlite3
from os.path import exists
from wikidata_local_reconciliator import WikidataLocalReconciliator

args = argparse.ArgumentParser(description="Search local wikidata db")
args.add_argument('name')
args.add_argument('-db', dest='db', metavar='filename', nargs=1, type=str,
                  help='the sqlite3 file with wikidata.',
                  required=True)

args = args.parse_args()
name = args.name
db = args.db[0]

if (not exists(db)):
    print(f"No file {db}. Please prepare the sqlite3 db with"
          "./bin/prepare_db.py -db {db} and then parse the wikidata dump.")
    exit(1)


reconciliator = WikidataLocalReconciliator(db_file=db)
res = reconciliator.ask(name, occupations=False)
print(name)
print(res)
exit(0)

connection = sqlite3.connect(db)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

for row in cursor.execute("""
        SELECT DISTINCT humans.* FROM humans
        LEFT JOIN names ON humans.id = human_id
        WHERE names.name = ?
        """, (name.lower(), )).fetchall():
    print(f"\n{row['id']} {row['wiki_id']}: {row['label']} ({row['description']})\n")
    for k in dict(row):
        print(f"{k}: {row[k]}")
