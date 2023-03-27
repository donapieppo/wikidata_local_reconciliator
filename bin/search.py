#!/usr/bin/env python3

import sys
import sqlite3
import json

connection = sqlite3.connect("data/wd.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

what = sys.argv[1]

for row in cursor.execute("""
        SELECT DISTINCT humans.* FROM humans
        LEFT JOIN names ON humans.id = human_id
        WHERE names.name LIKE ?
        COLLATE NOCASE
        """, ("%" + what + "%", )).fetchall():
    firstname = json.loads(row["labels"])[0]
    print(f"{row['id']} {row['wiki_id']}: {firstname}")
    print(row["description"])
