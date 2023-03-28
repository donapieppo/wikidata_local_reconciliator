#!/usr/bin/env python3

import json
import bz2
import sqlite3
from wikidata_db_reconciliation import WDHuman, WDItem, check_if_human

connection = sqlite3.connect("/home/backup/wd.db")
cursor = connection.cursor()


def save_human(wdhuman):
    cursor.execute("""
        INSERT INTO humans (
            wiki_id,
            viaf_id,
            qnames,
            qsurnames,
            labels,
            aliases,
            year_of_birth,
            year_of_death,
            description,
            occupations,
            wikipedia_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            wdhuman.wiki_id,
            (json.dumps(wdhuman.viaf_id) if wdhuman.viaf_id else None),
            json.dumps(wdhuman.qnames),
            json.dumps(wdhuman.qsurnames),
            json.dumps(list(wdhuman.labels)),
            json.dumps(list(wdhuman.aliases)),
            wdhuman.year_of_birth,
            wdhuman.year_of_death,
            wdhuman.description,
            json.dumps(wdhuman.occupations),
            wdhuman.wikipedia_url
            )
        )


# with bz2.open("/home/backup/latest-all.json.bz2", mode='rt') as f:
with open("/home/backup/test.json", mode='rt') as f:
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
            save_human(WDHuman(j))
            connection.commit()
        # else:
        #     wditem = WDItem(j)
        #     if wditem.labels:
        #         cursor.execute("""
        #           INSERT INTO wditems (wiki_id, labels) VALUES (?, ?)
        #           """, (wditem.wiki_id, json.dumps(list(wditem.labels))))
        #         connection.commit()

connection.commit()
connection.close()

# print(json.dumps(j, indent=2))
