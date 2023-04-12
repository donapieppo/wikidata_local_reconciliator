#!/usr/bin/env python3

import json
import sqlite3
from wikidata_local_reconciliation import WDHuman, WDItem, check_if_human

connection = sqlite3.connect("/home/backup/wd.db")
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
    n = json.loads(row['qnames']) if row['qnames'] else []
    s = json.loads(row['qsurnames']) if row['qsurnames'] else []
    if n:
        print(n)
        total += n
    if s:
        print(s)
        total += s
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
