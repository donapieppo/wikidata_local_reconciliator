import unittest

from wikidata_local_reconciliator import WikidataLocalReconciliator

reconciliator = WikidataLocalReconciliator(db_file='/home/backup/wd.db')


class TestWikidataLocalReconciliator(unittest.TestCase):
    def test_all_ok(self):
        res = reconciliator.ask('martin scorsese', 2000, 'film_director')
        self.assertEqual(res['wiki_id'], "Q41148")

    def test_strange_name(self):
        res = reconciliator.ask('  maRtin  scorsese   ', 2000, 'film_director')
        self.assertEqual(res['wiki_id'], "Q41148")

    def test_strange_name2(self):
        res = reconciliator.ask(' maRtin  (12) scorsese (1970-200)  ', 2000, 'film_director')
        self.assertEqual(res['wiki_id'], "Q41148")

    def test_strange_name3(self):
        res = reconciliator.ask(' maRtin-scorsese ', 2000, 'film_director')
        self.assertEqual(res['wiki_id'], "Q41148")

    def test_with_unidecode_name(self):
        res = reconciliator.ask(' maRtin-scorsésé ', 2000, 'film_director')
        self.assertEqual(res['wiki_id'], "Q41148")

    def test_wrong_year(self):
        res = reconciliator.ask('martin scorsese', 1925, 'film_director')
        self.assertEqual(res, None)

    def test_wrong_occupation(self):
        res = reconciliator.ask('martin scorsese', 2000, 'poet')
        self.assertEqual(res, None)

    def test_wrong_default_occupation(self):
        res = reconciliator.ask('achille occhetto')
        self.assertEqual(res, None)

    def test_any_occupation(self):
        res = reconciliator.ask('achille occhetto', occupations=False)
        self.assertEqual(res['wiki_id'], "Q340239")


if __name__ == '__main__':
    unittest.main()
