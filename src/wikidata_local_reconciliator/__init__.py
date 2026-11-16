import sqlite3
import re
import os
from unidecode import unidecode

from wikidata_occupation import WikidataOccupation

DEFAULT_DB_FILE = "wikidata.db"

# Il migliore candidato viene accettato solo se ha almeno AMBIGUITY_RATIO volte
# le referenze del secondo (es. 2 -> almeno il doppio). None disattiva il controllo.
AMBIGUITY_RATIO = 2
# Un nome di una sola parola ("martin", "jean") viene accettato solo se la persona
# è molto nota (Giotto, Caravaggio...). None disattiva il controllo.
SINGLE_WORD_MIN_REFERENCES = 50


class WikidataLocalReconciliator():
    def __init__(self, db_file=None,
                 ambiguity_ratio=AMBIGUITY_RATIO,
                 single_word_min_references=SINGLE_WORD_MIN_REFERENCES):
        if db_file is None:
            db_file = os.environ.get("WIKIDATA_DB", DEFAULT_DB_FILE)
        self.connection = sqlite3.connect(db_file)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.wd_occupation = WikidataOccupation()
        self.ambiguity_ratio = ambiguity_ratio
        self.single_word_min_references = single_word_min_references

    def close(self):
        self.connection.close()

    def add_occupation(self, name, wiki_id):
        self.wd_occupation.add_occupation(name, wiki_id)

    def check_year(self, row, year):
        """Returns True id checks if row['year_of_birth'] > year

        It usually cheks if the person was already born in the year of the opera
        """

        if year and row['year_of_birth']:
            return row['year_of_birth'] < year
        else:
            return(True)

    def clear_name(self, name, replace_dash=False, with_unidecode=False):
        """Clear the name and return it"""
        # fist lower the name since in db they are lowercase
        name = name.lower()
        # take off brackets (200xii)
        name = re.sub(r'\(.*?\)', '', name)
        # strip spaces and 2... spaces becomes one
        name = re.sub(r'\s{2,}', ' ', name).strip()
        if replace_dash:
            name = re.sub(r'-', ' ', name)
        if with_unidecode:
            name = unidecode(name)
        return(name)

    def check_name_from_wiki_id(self, wiki_id, name):
        """Check if human identified by wiki_id has the name"""
        res = self.cursor.execute("""
            SELECT id FROM names WHERE wiki_id = ? AND name = ?
            """, (wiki_id, name.lower())).fetchone()
        return(res)

    def get_by_wiki_id(self, wiki_id):
        res = self.cursor.execute("""
                SELECT * from humans WHERE wiki_id = ?
                """, (wiki_id, )).fetchone()
        return res if res else None

    def get_by_viaf_id(self, viaf_id):
        res = self.cursor.execute("""
            SELECT humans.* FROM humans
            LEFT JOIN viafs ON viafs.human_id = humans.id
            WHERE viafs.viaf_id = ?
            ORDER BY nreferences DESC
            """, (viaf_id, )).fetchone()
        return res if res else None

    def candidates(self, name, year=None, occupations=None):
        """Persone con quel nome che rispettano anno e occupazioni,
        una sola riga per persona, ordinate per nreferences decrescente."""
        name = self.clear_name(name)
        all_rows = self.cursor.execute("""
            SELECT DISTINCT humans.*, viafs.viaf_id FROM humans
            LEFT JOIN names ON humans.id = names.human_id
            LEFT JOIN viafs ON humans.id = viafs.human_id
            WHERE names.name = ?
            """, (name, )).fetchall()

        # la LEFT JOIN su viafs produce una riga per ogni VIAF della stessa persona:
        # teniamo una sola riga per wiki_id, altrimenti la persona "fa concorrenza" a se stessa
        by_wiki_id = {}
        for row in all_rows:
            row = dict(row)
            if not (self.wd_occupation.check(row, occupations) and self.check_year(row, year)):
                continue
            if row['wiki_id'] not in by_wiki_id:
                by_wiki_id[row['wiki_id']] = row

        return sorted(by_wiki_id.values(), key=lambda r: r['nreferences'] or 0, reverse=True)

    def is_confident(self, name, candidates):
        """True se il primo candidato è abbastanza affidabile da essere restituito."""
        best = candidates[0]
        best_refs = best['nreferences'] or 0

        if self.single_word_min_references is not None and len(name.split()) == 1:
            if best_refs < self.single_word_min_references:
                return False

        if self.ambiguity_ratio is not None and len(candidates) > 1:
            second_refs = candidates[1]['nreferences'] or 0
            if best_refs < self.ambiguity_ratio * second_refs:
                return False

        return True

    def search(self, name, year=None, occupations=None):
        """Il candidato migliore, oppure None se non c'è o se è ambiguo."""
        name = self.clear_name(name)
        candidates = self.candidates(name, year=year, occupations=occupations)
        if not candidates:
            return None
        if not self.is_confident(name, candidates):
            return None
        return candidates[0]

    def ask(self, name, year=None, occupations=None):
        if not name or not name.strip():
            return None

        # varianti del nome, dalla più fedele alla più permissiva, senza ripetizioni
        variants = []
        for options in ({}, {'replace_dash': True}, {'replace_dash': True, 'with_unidecode': True}):
            cname = self.clear_name(name, **options)
            if cname and cname not in variants:
                variants.append(cname)

        for cname in variants:
            res = self.search(cname, year=year, occupations=occupations)
            if res:
                return res
        return None
        
    def show_occupations(self, res):
        if res:
            print(res["occupations"])
            print(self.wd_occupation.describe(res["occupations"]))

    def show_res(self, res):
        if res:
            return(f"{res['wiki_id']}: {res['label']} ({res['year_of_birth']}) {res['description']} viaf: {res['viaf_id']}")
        else:
            return("No Result")
