#!/usr/bin/env python3

import json
from wikidata_db_reconciliation import WDHuman, WDItem, check_for_human

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
        else:
            wditem = WDItem(j)
            if wditem.name or wditem.surname:
                print(wditem)
