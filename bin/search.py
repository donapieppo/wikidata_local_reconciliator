#!/usr/bin/env python3

import sys
import sqlite3
import json

connection = sqlite3.connect("/home/backup/wd.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

what = sys.argv[1]

for row in cursor.execute("""
        SELECT DISTINCT humans.* FROM humans
        LEFT JOIN names ON humans.id = human_id
        WHERE names.name = ?
        COLLATE NOCASE
        """, (what, )).fetchall():
    print(f"\n{row['id']} {row['wiki_id']}: {row['label']} ({row['description']})\n")
    for k in dict(row):
        print(f"{k}: {row[k]}")
