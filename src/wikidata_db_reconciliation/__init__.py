# date of birth (P569) 
# date of death (P570) 
# ISNI (P213) 
# occupation (P106) 
# date of birth (P569) 
# date of death (Q18748141) 

QNAMES = {
        'P734',       # name
        'Q101352',    # family name (Q101352)
        'Q12308941',  # male given name (Q12308941)
        'Q11879590',  # female given name (Q11879590)
        }

QSURNAMES = {
        'P735'  # surname
        }

QNAMES_AND_SURNAMES = QNAMES.union(QSURNAMES)

# in order for description. First present wins.
languages = [
        'it',
        'en',
        'es',
        'fr',
        'de'
        ]


def check_if_human(j):
    for x in j['claims']['P31']:
        if x['mainsnak']['datavalue']['value']['id'] == 'Q5':
            return True
    return False


def extract_datavalue(j):
    try:
        if j['mainsnak']['snaktype'] == 'novalue':
            return None
        elif j['mainsnak']['datatype'] == 'external-id':
            return j['mainsnak']['datavalue']['value']
        elif j['mainsnak']['datatype'] == 'wikibase-item':
            return j['mainsnak']['datavalue']['value']['id']
        elif j['mainsnak']['datatype'] == 'time':
            return j['mainsnak']['datavalue']['value']['time']
        else:
            print(j['mainsnak'])
            exit(0) 
            return None
    except KeyError:
        # can happen instance of is not a valid qualifier for ....
        print(j["id"])
        print(j['mainsnak'])
        return None


class WDHuman:
    def __init__(self, j):
        self.json = j
        self.wiki_id = self.json["id"]

        self.labels = self.extract_labels()
        self.qnames = self.extract_qnames()
        self.qsurnames = self.extract_qsurnames()
        self.viaf_id = self.extract_viafid()

        self.year_of_birth = self.extract_year_of_birth()
        self.description = self.extract_description()

    def extract_viafid(self):
        if 'P214' in self.json['claims']:
            res = [extract_datavalue(x) for x in self.json['claims']['P214']]
            return (None if res == [None] else res)

    def extract_labels(self):
        res = set()
        for lang in languages:
            if lang in self.json['labels']:
                label = self.json['labels'][lang]['value']
                if label:
                    res.add(label)
        return (None if res == [None] else res)

    def extract_qnames(self):
        for n in QSURNAMES:
            if n in self.json['claims']:
                return [extract_datavalue(x) for x in self.json['claims'][n]]

    def extract_qsurnames(self):
        for n in QNAMES:
            if n in self.json['claims']:
                return [extract_datavalue(x) for x in self.json['claims'][n]]

    # return int with sign
    def extract_year_of_birth(self):
        if 'P569' in self.json['claims']:
            date = extract_datavalue(self.json['claims']['P569'][0])
            # "+1732-02-22T00:00:00Z"
            # "-0401-01-01T00:00:00Z"
            if date and len(date) == 21:
                return date[0:5]
            else:
                return None

    # first description in languages in order
    def extract_description(self):
        for lang in languages:
            if lang in self.json['descriptions']:
                return self.json['descriptions'][lang]["value"]

    def __str__(self):
        return("human id: " + str(self.wiki_id) +
               " qnames: " + str(self.qnames) +
               " qsurnames: " + str(self.qsurnames) + 
               " labels: " + str(self.labels) +
               " viafid: " + str(self.viaf_id))


class WDItem:
    def __init__(self, j):
        self.json = j
        self.wiki_id = self.json["id"]
        self.labels = self.extract_labels()

    # {'mainsnak': {... 'datavalue': {'value': {... 'id': 'Q5'} ...
    def extract_labels(self):
        for x in self.json['claims']['P31']:
            if x['mainsnak']['datavalue']['value']['id'] in QNAMES_AND_SURNAMES:
                labels = self.json['labels']
                res = set()
                for lang in languages:
                    if (lang in labels):
                        res.add(labels[lang]['value'])
                return res
        return None

    def __str__(self):
        return("wikiitem id: " + str(self.wiki_id) +
               " labels: " + str(self.labels))
