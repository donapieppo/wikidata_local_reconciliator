#!/usr/bin/env python3

import argparse
import json
import sqlite3
from os.path import exists

args = argparse.ArgumentParser(description='Add qnames and qsurnames in names.')

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
cursor_name = connection.cursor()
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


def add_wdname(tot, qval):
    if not qval:
        return tot

    cursor_wditem.execute("SELECT * FROM wditems WHERE wiki_id = ?", (qval,))
    res = cursor_wditem.fetchone()

    if res and res['labels']:
        if tot == "":
            tot = res['labels']
        else:
            tot = tot + " " + res['labels']

    return tot.lower()

cursor_human.execute("SELECT * from humans")

def add_wdname(tot, qval):
    if not qval:
        return tot

    cursor_wditem.execute("SELECT * FROM wditems WHERE wiki_id = ?", (qval,))
    row = cursor_wditem.fetchone()

    if row:
        labels = json.loads(row['labels'])
        print(f"{qval} -> {labels}")
        if tot == "":
            tot = labels[0]
        else:
            tot = f"{tot} {labels[0]}"

    return tot.lower()

for row in cursor_human:
    print(f"{row['id']} --- qnames: {row['qnames']} --- qsurnames: {row['qsurnames']} --- {row['wiki_id']}")

    qnames = json.loads(row['qnames']) if row['qnames'] != 'null' else []
    qsurnames = json.loads(row['qsurnames']) if row['qsurnames'] != 'null' else []

    tot = ""
    for qname in qnames:
        tot = add_wdname(tot, qname)
    for qsurname in qsurnames:
        tot = add_wdname(tot, qsurname)

    cursor_name.execute("SELECT count(*) as c FROM names "
                        "WHERE name = ? AND human_id = ? LIMIT 1",
                        (tot, row['id']))
    res = cursor_name.fetchone()

    if res['c'] == 0:
        print(tot)
    input(".")

connection.commit()
connection.close()
