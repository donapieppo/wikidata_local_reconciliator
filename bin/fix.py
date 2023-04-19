#!/usr/bin/env python3

import argparse
import json
import sqlite3
from wikidata_local_reconciliation import WDHuman, WDItem, check_if_human
from os.path import exists

args = argparse.ArgumentParser(description='Parse a wikidata gz dump file and save in sqlite3 db.')

args.add_argument('-db', metavar='filename', nargs=1, type=str,
                   help='the sqlite3 file to read/rwite data.',
                   required=True)

args = args.parse_args()
db = args.db[0]

if (not exists(db)):
    print(f"No file {db}.")
    exit(1)


connection = sqlite3.connect(db)
connection.row_factory = sqlite3.Row
cursor_human = connection.cursor()
cursor_wditem = connection.cursor()


def update_human(human_id, name, surname):
    if not (human_id and name and surname):
        return False

    cursor_human.execute("""
        UPDATE humans SET (
            name=?
            surname=?
            ) WHERE id=?
        """, (name, surname, human_id))
    connection.commit()
    return cursor_human.lastrowid


cursor_human.execute("SELECT * from humans")

for row in cursor_human:
    print(f"--- row {row['id']} ----")
    print(row['qnames'])
    print(row['qsurnames'])
    print("--- end row ----")

    total = []
    names = json.loads(row['qnames']) if row['qnames'] else []
    surnames = json.loads(row['qsurnames']) if row['qsurnames'] else []

    if names:
        print(names)
        total += names
    if surnames:
        print(surname)
        total += surnames
    print(total)
    print("----")
    for qname in total:
        cursor_wditem.execute("SELECT * from wditems where wiki_id = ?", (qname,))
        name = " ".join([item['labels'] for item in cursor_wditem])
        print(name)
        # if res and len(res) > 0:
    input(".")

#connection.commit()
#connection.close()
