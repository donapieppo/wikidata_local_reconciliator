#!/usr/bin/env python3

import sys
import sqlite3
import json

connection = sqlite3.connect("data/wd.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

what = sys.argv[1]

for row in cursor.execute("""
        SELECT * FROM humans left join names on humans.id = human_id WHERE names.name LIKE ?
        """, ("%" + what + "%", )).fetchall():
    print(str(row["id"]) + "  " + str(json.loads(row["labels"])))
    print(row["description"])
