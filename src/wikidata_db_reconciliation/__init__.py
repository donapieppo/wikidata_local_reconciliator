# date of birth (P569)
# date of death (P570)
# ISNI (P213)
# occupation (P106)
# date of birth (P569)
# date of death (P570)
# work period (start) (P2031)
# work period (end) (P2032)

# profession (Q28640)
# occupation (Q12737077)
# field of work (P101)

OCCUPATIONS = {
        'Q28640',    # profession (Q28640)
        'Q12737077'  # occupation (Q12737077)
        }

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
QNAMES_AND_SURNAMES_AND_OCCUPATION = QNAMES_AND_SURNAMES.union(OCCUPATIONS)

# in order for description. First present wins.
languages = [
        'it',
        'en',
        'es',
        'fr',
        'de'
        ]


def extract_value(json_obj, path):
    keys = path.split('.')
    current = json_obj
    for key in keys:
        try:
            current = current[key]
        except (KeyError, TypeError):
            return None
    return current


def check_value(json_obj, path, expected):
    return (extract_value(json_obj, path) == expected)


def check_if_human(j):
    for x in j['claims']['P31']:
        try:
            return check_value(x, 'mainsnak.datavalue.value.id', 'Q5')
        except (KeyError, TypeError):
            return False


def extract_datavalue(j):
    try:
        if check_value(j, 'mainsnak.snaktype', 'novalue'):
            return None
        elif check_value(j, 'mainsnak.datatype', 'external-id'):
            return extract_value(j, 'mainsnak.datavalue.value')
        elif check_value(j, 'mainsnak.datatype', 'wikibase-item'):
            return extract_value(j, 'mainsnak.datavalue.value.id')
        elif check_value(j, 'mainsnak.datatype', 'time'):
            return extract_value(j, 'mainsnak.datavalue.value.time')
        else:
            print(j['mainsnak'])
            exit(0) 
            return None
    except (KeyError, TypeError):
        # can happen instance of is not a valid qualifier for ....
        print(j["id"])
        print(j['mainsnak'])
        return None


class WDHuman:
    def __init__(self, j):
        self.json = j
        self.wiki_id = self.json["id"]

        self.labels = self.extract_labels()
        self.label = self.extract_labels(first=True)
        self.aliases = self.extract_aliases()
        self.qnames = self.extract_qnames()
        self.qsurnames = self.extract_qsurnames()
        self.viaf_id = self.extract_viafid()

        self.year_of_birth = self.extract_year('P569')
        self.year_of_death = self.extract_year('P570')
        self.year_work_start = self.extract_year('P2031')
        self.year_work_end = self.extract_year('P2032')
        self.description = self.extract_description()
        self.occupations = self.extract_occupations()

        # if all
        # self.wikipedia_names = self.extract_wikipedia_names()
        self.wikipedia_url = self.extract_wikipedia_url()

    def extract_viafid(self):
        if 'P214' in self.json['claims']:
            res = [extract_datavalue(x) for x in self.json['claims']['P214']]
            return (None if res == [None] else res)

    def extract_labels(self, first=False):
        res = set()
        for lang in languages:
            if lang in self.json['labels']:
                label = self.json['labels'][lang]['value']
                if label:
                    if first:
                        return str(label)
                    res.add(label)
        if first:
            return ''
        return (None if res == [None] else res)

    # for now direrent from labels. 
    def extract_aliases(self):
        res = set()
        for lang in languages:
            if lang in self.json['aliases']:
                for alias in self.json['aliases'][lang]:
                    label = alias['value']
                    if label:
                        res.add(label)
        return (None if res == [None] else res)

    # https://it.wikipedia.org/wiki
    def extract_wikipedia_names(self):
        res = {}
        for lang in languages:
            if lang + 'wiki' in self.json['sitelinks']:
                res[lang] = self.json['sitelinks'][lang + 'wiki']['title']
        return res

    # extract first
    def extract_wikipedia_url(self):
        for lang in languages:
            if lang + 'wiki' in self.json['sitelinks']:
                title = self.json['sitelinks'][lang + 'wiki']['title']
                if title:
                    return 'https://' + lang + '.wikipedia.org/wiki/' + title.replace(' ', '_')

    def extract_qnames(self):
        for n in QSURNAMES:
            if n in self.json['claims']:
                return [extract_datavalue(x) for x in self.json['claims'][n]]

    def extract_qsurnames(self):
        for n in QNAMES:
            if n in self.json['claims']:
                return [extract_datavalue(x) for x in self.json['claims'][n]]

    # return int with sign
    def extract_year(self, p):
        if p in self.json['claims']:
            date = extract_datavalue(self.json['claims'][p][0])
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

    def extract_occupations(self):
        if 'P106' in self.json['claims']:
            res = [extract_value(x, "mainsnak.datavalue.value.id") for x in self.json['claims']['P106']]
            return (None if res == [None] else res)

    def __str__(self):
        return("human id: " + str(self.wiki_id) +
               " label: " + str(self.label) +
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
            elif x['mainsnak']['datavalue']['value']['id'] in OCCUPATIONS:
                labels = self.json['labels']
                res = set()
                for lang in ['it', 'en']:
                    if (lang in labels):
                        res.add(labels[lang]['value'])
                return res
        return None

    def __str__(self):
        return("wikiitem id: " + str(self.wiki_id) +
               " labels: " + str(self.labels))
