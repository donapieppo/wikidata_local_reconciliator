import json
from wikidata_json_helpers import extract_value, extract_datavalue

QNAMES = {
    'P734',       # name
    'Q101352',    # family name (Q101352)
    'Q12308941',  # male given name (Q12308941)
    'Q11879590',  # female given name (Q11879590)
}

QSURNAMES = {
    'P735'  # surname
}

class WikidataHuman:
    def __init__(self, j, languages):
        self.json = j
        self.languages = languages
        self.wiki_id = self.json["id"]

        self.label = self.extract_label()
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
        self.nreferences = self.count_references()

    def extract_viafid(self):
        if 'P214' in self.json['claims']:
            x = self.json['claims']['P214'][0]
            if x:
                return extract_datavalue(x)
            #
            # res = [extract_datavalue(x) for x in self.json['claims']['P214']]
            # return (None if res == [None] else res)

    def extract_label(self):
        for lang in self.languages:
            if lang in self.json['labels']:
                label = self.json['labels'][lang]['value']
                if label:
                    return str(label)
                
    # https://it.wikipedia.org/wiki
    def extract_wikipedia_names(self):
        res = {}
        for lang in self.languages:
            if lang + 'wiki' in self.json['sitelinks']:
                res[lang] = self.json['sitelinks'][lang + 'wiki']['title']
        return res

    # extract first
    def extract_wikipedia_url(self):
        for lang in self.languages:
            field = lang + 'wiki'
            if field in self.json['sitelinks']:
                title = self.json['sitelinks'][field]['title']
                if title:
                    title = title.replace(' ', '_')
                    return f"https://{lang}.wikipedia.org/wiki/{title}"

    def extract_qnames(self):
        """ extract the first available from mames, male given name.... """
        for n in QNAMES:
            if n in self.json['claims']:
                return [extract_datavalue(x) for x in self.json['claims'][n]]

    def extract_qsurnames(self):
        """ as extract_qnames also if in this case QSURNAMES in 1 element. """
        for n in QSURNAMES:
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
        for lang in self.languages:
            if lang in self.json['descriptions']:
                return self.json['descriptions'][lang]["value"]

    def extract_occupations(self):
        if 'P106' in self.json['claims']:
            res = [extract_value(x, "mainsnak.datavalue.value.id") for x in self.json['claims']['P106']]
            return (None if res == [None] else res)

    def count_references(self):
        n = 0
        # for interest in ["P31", "P569"]:
        #     if interest in self.json['claims']:
        if "P800" in self.json['claims']:
            n = len(self.json['claims']["P800"])
        return n

    def save(self, cursor):
        cursor.execute("""
            INSERT INTO humans (
                wiki_id,
                viaf_id,
                qnames,
                qsurnames,
                label,
                year_of_birth,
                year_of_death,
                description,
                occupations,
                wikipedia_url,
                nreferences
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.wiki_id,
                (json.dumps(self.viaf_id) if self.viaf_id else None),
                json.dumps(self.qnames),
                json.dumps(self.qsurnames),
                self.label,
                self.year_of_birth,
                self.year_of_death,
                self.description,
                json.dumps(self.occupations),
                self.wikipedia_url,
                self.nreferences
                )
            )

    def __str__(self):
        return("human id: " + str(self.wiki_id) +
               " label: " + str(self.label) +
               " description: " + str(self.description))

