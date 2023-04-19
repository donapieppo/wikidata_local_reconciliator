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
# notable work (P800)

import sqlite3
from wikidata_json_helpers import check_value, extract_datavalue
from wikidata_human import WikidataHuman
from wikidata_item import WikidataItem

DEFAULT_LANGUAGES = ['it', 'en', 'es', 'fr', 'de']

class WikidataLocalParser:
    """ languages order for description. First present wins. """
    def __init__(self, db, languages=None):
        self.db = db
        self.languages = languages if languages else DEFAULT_LANGUAGES
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def __check_if_human(self, j):
        for x in j['claims']['P31']:
            try:
                return check_value(x, 'mainsnak.datavalue.value.id', 'Q5')
            except (KeyError, TypeError):
                return False

    def __save_names(self, human_id, j):
        names = set()
        for lang in self.languages:
            if lang in j['labels']:
                label = j['labels'][lang]['value']
                if label:
                    names.add(label)

            if lang in j['aliases']:
                for alias in j['aliases'][lang]:
                    label = alias['value']
                    if label:
                        names.add(label)

        for name in names:
            self.cursor.execute("""
              INSERT INTO names (human_id, name)
              VALUES (?, ?)
            """, (human_id, name.lower()))

    def __save_viafs(self, human_id, wiki_id, j):
        if 'P214' in j['claims']:
            for x in j['claims']['P214']:
                viaf_id = extract_datavalue(x)
                if viaf_id:
                    self.cursor.execute("""
                        INSERT INTO viafs (human_id, wiki_id, viaf_id)
                        VALUES (?, ?, ?)
                    """, (human_id, wiki_id, viaf_id))


    def save(self, j):
        if ('P31' not in j['claims']):
            return None  # P31 istance of

        if self.__check_if_human(j):
            wdhuman = WikidataHuman(j, self.languages)
            wdhuman.save(self.cursor)
            self.connection.commit()
            human_id = self.cursor.lastrowid
            print(wdhuman)

            self.__save_names(human_id, j)
            self.__save_viafs(human_id, wdhuman.wiki_id, j)
        else:
            wditem = WikidataItem(j, self.languages)
            if wditem.labels:
                print(wditem)
                wditem.save(self.cursor)

    def close(self):
        """ Close db connection. """
        self.connection.commit()
        self.connection.close()
