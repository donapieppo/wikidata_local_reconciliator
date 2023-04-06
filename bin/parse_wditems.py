#!/usr/bin/env python3

import sys
import json
import bz2
import sqlite3
from os.path import exists

from wikidata_local_reconciliation import WDHuman, WDItem, check_if_human

if len(sys.argv) < 2:
    print("Need file name")
    exit(0)

FILE = sys.argv[1]

if (not exists(FILE)):
    print(f"No file {FILE}")
    exit(1)

FIRST_FILE = '0000' in FILE

connection = sqlite3.connect("/home/backup/wd.db")
cursor = connection.cursor()


def update_human(human_id, name, surname):
    if not (human_id and name and surname):
        return False

    cursor.execute("""
        UPDATE humans SET (
            name=?
            surname=?
            ) WHERE id=?
        """, (name, surname, human_id))
    connection.commit()
    return cursor.lastrowid


with bz2.open(FILE, mode='rt') as f:
    if FIRST_FILE:
        f.read(2)  # skip first two bytes: "{\n"
    i = 0
    for line in f:
        print(f"{i}   {line[15:35]}")
        i += 1
        j = json.loads(line.rstrip(',\n'))
        if ('P31' not in j['claims']):
            continue  # P31 istance of

        if not check_if_human(j):
            wditem = WDItem(j, first_label=True)
            if wditem.labels:
                print(wditem)
                cursor.execute("""
                    INSERT INTO wditems (wiki_id, labels) VALUES (?, ?)
                """, (wditem.wiki_id, wditem.labels))
                connection.commit()

connection.close()

# print(json.dumps(j, indent=2))
