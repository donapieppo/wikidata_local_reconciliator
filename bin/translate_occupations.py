#!/usr/bin/env python3

import sys
from wikidata_occupation import WikidataOccupation

if len(sys.argv) < 2:
    print("""
Esempi:
  - translate_occupation.py '["Q1028181", "Q483501"]'
  - translate_occupation.py "Q1028181, Q483501"
  - translate_occupation.py "artist, film_director"
""")

q = sys.argv[1]

wdo = WikidataOccupation()
print(wdo.describe(q))
