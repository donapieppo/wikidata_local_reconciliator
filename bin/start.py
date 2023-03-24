#!/usr/bin/env python3

import json
import bz2
import sqlite3
from wikidata_db_reconciliation import WDHuman, WDItem, check_if_human

connection = sqlite3.connect("data/wd.db")
cursor = connection.cursor()

with open("data/test.json", mode='rt') as f:
#with bz2.open("/home/backup/wikidata-20220103-all.json.gz", mode='rt') as f:
    f.read(2)  # skip first two bytes: "{\n"
    i = 0
    for line in f:
        print(i)
        i += 1
        try:
            j = json.loads(line.rstrip(',\n'))
            if ('P31' not in j['claims']):
                continue  # P31 istance of
        except json.decoder.JSONDecodeError:
            continue

        if check_if_human(j):
            wdhuman = WDHuman(j)
            # print(wdhuman)
            cursor.execute("""INSERT INTO humans (wiki_id, viaf_id, qnames, qsurnames, labels, year_of_birth, description, occupations)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           (wdhuman.wiki_id,
                           (json.dumps(wdhuman.viaf_id) if wdhuman.viaf_id else None), 
                           json.dumps(wdhuman.qnames), 
                           json.dumps(wdhuman.qsurnames),
                           json.dumps(list(wdhuman.labels)),
                           wdhuman.year_of_birth,
                           wdhuman.description,
                           json.dumps(wdhuman.occupations)))
            connection.commit()
        else:
            wditem = WDItem(j)
            if wditem.labels:
                cursor.execute("INSERT INTO wditems (wiki_id, labels) VALUES (?, ?)",
                               (wditem.wiki_id,
                                json.dumps(list(wditem.labels))))
                connection.commit()

connection.commit()
connection.close()

# print(json.dumps(j, indent=2))
