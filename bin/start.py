#!/usr/bin/env python3

import json
import sqlite3
from wikidata_db_reconciliation import WDHuman, WDItem, check_for_human

connection = sqlite3.connect("data/wd.db")
cursor = connection.cursor()

with open("data/test.json", mode='rt') as f:
    f.read(2)  # skip first two bytes: "{\n"
    i = 0
    for line in f:
        # print(i)
        i += 1
        try:
            j = json.loads(line.rstrip(',\n'))
            if not ('claims' in j):
                continue
            if not ('P31' in j['claims']):
                continue  # P31 istance of
        except json.decoder.JSONDecodeError:
            continue

        if check_for_human(j):
            wdhuman = WDHuman(j)
            print(wdhuman)
            print(wdhuman.wiki_id, wdhuman.viaf_id, json.dumps(wdhuman.qnames), json.dumps(wdhuman.qsurnames))
            cursor.execute("INSERT INTO humans (wiki_id, viaf_id, qnames, qsurnames, labels) VALUES (?, ?, ?, ?, ?)",
                            (wdhuman.wiki_id, 
                             json.dumps(wdhuman.viaf_id), 
                             json.dumps(wdhuman.qnames), 
                             json.dumps(wdhuman.qsurnames),
                             json.dumps(list(wdhuman.labels))))
            connection.commit()
        else:
            wditem = WDItem(j)
            if wditem.labels:
                print(wditem)
                cursor.execute("INSERT INTO wditems (wiki_id, labels) VALUES (?, ?)",
                                (wditem.wiki_id, 
                                 json.dumps(wditem.labels)))
                connection.commit()
            #if wditem.wiki_id == 'Q24223':
            #    print(json.dumps(j, indent=2))
