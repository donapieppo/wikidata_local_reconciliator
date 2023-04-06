#!/usr/bin/env python3

import json
import sqlite3
from wikidata_local_reconciliation import WDHuman, WDItem, check_if_human

connection = sqlite3.connect("/home/backup/wd.db")
connection.row_factory = sqlite3.Row
cursor_human = connection.cursor()
cursor_wditem = connection.cursor()

cursor_human.execute("SELECT * from humans")

for row in cursor_human:
    print(f"--- row {row['id']} ----")
    print(row['qnames'])
    print(row['qsurnames'])
    print("--- end row ----")
    total = []
    n = [] if row['qnames'] == '[null]' else json.loads(row['qnames'])
    s = [] if row['qsurnames'] == '[null]' else json.loads(row['qsurnames'])
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
