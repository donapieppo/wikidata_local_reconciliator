#!/usr/bin/env python3

import json
import sqlite3
from wikidata_db_reconciliation import WDHuman, WDItem, check_if_human

connection = sqlite3.connect("data/wd.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
cursor2 = connection.cursor()

cursor.execute("SELECT * from humans")

for row in cursor:
    for x in json.loads(row['labels']):
        print(x)
        cursor2.execute("""
          INSERT INTO names (human_id, name, wiki_id) VALUES (?, ?, ?)
          """, (row['id'], x, row['wiki_id']))
    continue

    print("------")
    print(row['qnames'])
    if row['qnames'] == 'null':
        continue
    for qname in json.loads(row['qnames']):
        cursor2.execute("SELECT * from wditems where wiki_id = ?", (qname,))
        res = cursor2.fetchone()
        if res and len(res) > 0:
            print(res['labels'])

connection.commit()
connection.close()
