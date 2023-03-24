# wikidata database reconciliation

From a wikidata database dump prepare for reconciliation

## Start

Visit [https://www.wikidata.org/wiki/Wikidata:Database_download] and get
(better vith torrent) latest json.bz2

To do some testing

```bash
zcat /home/backup/wikidata-20220103-all.json.gz | head -5000 > data/test.json
```

and then

```bash
./bin/start.py
```


Create a `data/wd.db` with this schema:

```sql
CREATE TABLE humans (
  id INTEGER PRIMARY KEY,
  wiki_id TEXT,
  viaf_id TEXT,
  qnames TEXT,
  qsurnames TEXT,
  name TEXT,
  surname TEXT,
  labels TEXT,
  year_of_birth INT,
  description TEXT,
  occupations TEXT
);

CREATE UNIQUE INDEX idx_humans_wid ON humans (wiki_id);
CREATE INDEX idx_humans_viafid ON humans (viaf_id);

CREATE TABLE names (
  id INTEGER PRIMARY KEY,
  human_id INTEGER,
  name TEXT,
  wiki_id TEXT
);

CREATE INDEX idx_names_name ON names (name);
CREATE INDEX idx_names_human ON names (human_id);

CREATE TABLE wditems (
  id INTEGER PRIMARY KEY,
  wiki_id TEXT, 
  labels TEXT
);

CREATE UNIQUE INDEX idx_wditems_wid ON wditems (wiki_id);
```

`humans` on the first pass is filled with `qnames` and `qsurnames` which are the wikidata ids of name and surname of the human.

  - 'P734' (name)
  - 'Q101352' (family name)
  - 'Q12308941' (male given name)
  - 'Q11879590' (female given name)
  - 'P735' (surname)

For example Douglas Adams has wikidata_id: Q42 

  - qnames: `['Q463035', 'Q19688263']` 
  - qsurnames: `['Q351735']`

since `Q463035` -> `Douglas` but on the first pass we don't know. 
We have to reach the item `Q463035` on the wikidata dump to register 
it in the `wditems` table.

## Credits and other stuff

  - [https://akbaritabar.netlify.app/how_to_use_a_wikidata_dump] uses pydash to read json data more 

