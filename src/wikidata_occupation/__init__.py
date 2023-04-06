import json

OCCUPATIONS = {
        'artist': 'Q483501',
        'film_director': 'Q2526255',
        'painter': 'Q1028181',
        'writer': 'Q36180',
        'novelist': 'Q6625963',
        'video_artist': 'Q18216771',
        'photographer': 'Q33231',
        'sound_artist': 'Q19850998',
        'theatrical_director': 'Q3387717',
        'lyricist': 'Q822146',
        'journalist': 'Q1930187',
        'poet': 'Q49757',
        'painter': 'Q1028181',
        'actor': 'Q33999'
}


class WikidataOccupation():
    def __init__(self):
        self.occupations_by_name = OCCUPATIONS
        self.occupations_by_qcode = {value: key for key, value in OCCUPATIONS.items()}
        self.qcodes = set(OCCUPATIONS.values())

    def get_name_by_qcode(self, q):
        if q in self.occupations_by_qcode:
            return self.occupations_by_qcode[q]
        return None

    def get_qcode_by_name(self, n):
        if n in self.occupations_by_name:
            return self.occupations_by_name[n]
        return None

    def list_occupations(self):
        print(self.occupations_by_name)
        print(self.occupations_by_qcode)

    # True / False
    def check(self, row, occupations):
        if 'occupations' not in row:
            return False
        if not row['occupations'] or row['occupations'] == 'null':
            return False

        if occupations:
            occupations = occupations.split(', ')
            occupations = [OCCUPATIONS[k] for k in occupations]
        else:
            occupations = self.qcodes

        row['occupations'] = set(json.loads(row['occupations']))
        return len(row['occupations'].intersection(occupations)) > 0 

    def describe(self, names):
        """ can receve json.dump of array of occupatons or a list"""

        if names[0] == '[':
            names = json.loads(names)
        else:
            names = names.split(', ')

        if names[0][0] == 'Q':
            return([self.get_name_by_qcode(name) for name in names])
        return([self.get_qcode_by_name(name) for name in names])
