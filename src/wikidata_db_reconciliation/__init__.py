# date of birth (P569) 
# date of death (P570) 
# ISNI (P213) 
# occupation (P106) 

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

languages = [
        'en',
        'it',
        'es',
        'fr',
        'de'
        ]


def check_for_human(j):
    for x in j['claims']['P31']:
        if x['mainsnak']['datavalue']['value']['id'] == 'Q5':
            return True
    return False


def get_datavalue(j):
    if j['mainsnak']['snaktype'] == 'novalue':
        return None
    elif j['mainsnak']['datatype'] == 'external-id':
        return j['mainsnak']['datavalue']['value']
    elif j['mainsnak']['datatype'] == 'wikibase-item':
        return j['mainsnak']['datavalue']['value']['id']
    else:
        print(j['mainsnak'])
        exit(0)
        return None


class WDHuman:
    def __init__(self, j):
        self.json = j
        self.wiki_id = self.json["id"]
        self.labels = set()
        for l in languages:
            self.labels.add(self.get_label(l))

        self.qnames = self.get_qnames()
        self.qsurnames = self.get_qsurnames()
        self.viaf_id = self.get_viafid()

    def get_viafid(self):
        if 'P214' in self.json['claims']:
            return [get_datavalue(x) for x in self.json['claims']['P214']]

    def get_label(self, lang):
        if lang in self.json['labels']:
            return self.json['labels'][lang]['value']
        else:
            return None

    def get_qnames(self):
        for n in QSURNAMES:
            if n in self.json['claims']:
                return [get_datavalue(x) for x in self.json['claims'][n]]

    def get_qsurnames(self):
        for n in QNAMES:
            if n in self.json['claims']:
                return [get_datavalue(x) for x in self.json['claims'][n]]

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
        self.labels = self.get_labels()

    # {'mainsnak': {... 'datavalue': {'value': {... 'id': 'Q5'} ...
    def get_labels(self):
        for x in self.json['claims']['P31']:
            if x['mainsnak']['datavalue']['value']['id'] in QNAMES_AND_SURNAMES:
                print("OK")
                return self.json['labels']

    def __str__(self):
        return("wikiitem id: " + str(self.wiki_id) +
               " labels: " + str(self.labels))
