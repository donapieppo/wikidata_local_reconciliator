#!/usr/bin/env python3

import json
import bz2
import sqlite3
from wikidata_db_reconciliation import WDHuman, WDItem, check_if_human

connection = sqlite3.connect("/home/backup/wd.db")
cursor = connection.cursor()


def save_human(wdhuman):
    print(wdhuman)
    cursor.execute("""
        INSERT INTO humans (
            wiki_id,
            viaf_id,
            qnames,
            qsurnames,
            label,
            year_of_birth,
            year_of_death,
            description,
            occupations,
            wikipedia_url,
            nreferences
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            wdhuman.wiki_id,
            (json.dumps(wdhuman.viaf_id) if wdhuman.viaf_id else None),
            json.dumps(wdhuman.qnames),
            json.dumps(wdhuman.qsurnames),
            wdhuman.label,
            wdhuman.year_of_birth,
            wdhuman.year_of_death,
            wdhuman.description,
            json.dumps(wdhuman.occupations),
            wdhuman.wikipedia_url,
            wdhuman.nreferences
            )
                  )
    connection.commit()
    return cursor.lastrowid


def save_names(human_id, wdhuman):
    for name in wdhuman.labels.union(wdhuman.aliases):
        cursor.execute("""
          INSERT INTO names (human_id, wiki_id, name)
          VALUES (?, ?, ?)
        """, (human_id, wdhuman.wiki_id, name))


# with bz2.open("/home/backup/latest-all.json.bz2", mode='rt') as f:
with open("/home/backup/test.json", mode='rt') as f:
    f.read(2)  # skip first two bytes: "{\n"
    i = 0
    for line in f:
        print(i)
        i += 1
        j = json.loads(line.rstrip(',\n'))
        if ('P31' not in j['claims']):
            continue  # P31 istance of

        if check_if_human(j):
            wdhuman = WDHuman(j)
            human_id = save_human(wdhuman)
            save_names(human_id, wdhuman)
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
