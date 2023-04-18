import unittest
import json
import os, sys

from wikidata_json_helpers import extract_datavalue, extract_value, check_value

with open(os.path.join(sys.path[0], "test.json")) as f:
    J = json.load(f)

class TestWikidataJsonHelpers(unittest.TestCase):
    def test_extract_value(self):
        v = extract_value(J, "type")
        self.assertEqual(v, "item")

    def test_extract_value_multi(self):
        v = extract_value(J, "labels.en.value")
        self.assertEqual(v, "Andrei Tarkovsky")

    def test_extract_datavalue(self):
       v = extract_datavalue(J['claims']['P214'][0])
       self.assertEqual(v, "34515002")


if __name__ == '__main__':
    unittest.main()
