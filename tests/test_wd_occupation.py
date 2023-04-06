import unittest

from wikidata_occupation import WikidataOccupation

occupation = WikidataOccupation()


class TestOccupation(unittest.TestCase):
    def test_get_name_by_qcode(self):
        # Q1028181 -> painter
        self.assertEqual(occupation.get_name_by_qcode('Q1028181'), 'painter')

    def test_get_qcode_by_name(self):
        # painter -> Q1028181
        self.assertEqual(occupation.get_qcode_by_name('painter'), 'Q1028181')

    def test_check_with_no_field(self):
        self.assertEqual(occupation.check({'name': 'pippo'}, None), False)

    def test_check_with_null_field(self):
        self.assertEqual(occupation.check({'occupations': 'null'}, None), False)

    def test_check_correct(self):
        r = occupation.check({'occupations': '["Q1028181"]'}, 'painter')
        self.assertEqual(r, True)

    def test_check_correct2(self):
        r = occupation.check({'occupations': '["Q1028181"]'}, 'poet')
        self.assertEqual(r, False)

    def test_check_correct3(self):
        r = occupation.check({'occupations': '["Q1028181"]'}, 'poet, painter')
        self.assertEqual(r, True)

    def test_check_correct4(self):
        r = occupation.check({'occupations': '["Q1028181", "Q1111"]'}, 'poet, painter')
        self.assertEqual(r, True)


if __name__ == '__main__':
    unittest.main()
