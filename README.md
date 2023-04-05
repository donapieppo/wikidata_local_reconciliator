# Wikidata Local Reconciliation

From a wikidata database dump build a sqlite3 db useful for humans reconciliation.

From the wikidata dump we take all names and aliases of humans(Q5) with all occupations, birth and death dates and some "references number" 
in order to query a wikidata id given a name.


## Start

Visit [https://www.wikidata.org/wiki/Wikidata:Database_download] and get
latest json.bz2. You can also split it while downloading

```
mkdir wikidata
wget -O - https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2 | bzcat | split -l 100000 -d -a 4 --filter='bzip2 > wikidata/$FILE.json.bz2' - split-
```

If you already have downloaded the dump, you can just split with:

```bash
mkdir wikidata
bzcat latest-all.json.bz2 | split -l 100000 -d -a 4 --filter='bzip2 > wikidata/$FILE.json.bz2' - split-
```

Create a `data/wd.db` sqlite3 database with this schema:

```sql
CREATE TABLE humans (
  id INTEGER PRIMARY KEY,
  wiki_id TEXT,
  viaf_id TEXT,
  qnames TEXT,
  qsurnames TEXT,
  name TEXT,
  surname TEXT,
  label TEXT,
  year_of_birth INT,
  year_of_death INT,
  description TEXT,
  occupations TEXT,
  wikpedia_url TEXT,
  nreferences INT
);

CREATE UNIQUE INDEX idx_humans_wid ON humans (wiki_id);
CREATE INDEX idx_humans_viafid ON humans (viaf_id);

CREATE TABLE names (
  id INTEGER PRIMARY KEY,
  human_id INTEGER,
  wiki_id TEXT,
  name TEXT
);

CREATE INDEX idx_names_name ON names (name);
CREATE INDEX idx_names_human ON names (human_id);

CREATE TABLE wditems (
  id INTEGER PRIMARY KEY,
  wiki_id TEXT, 
  labels TEXT
);

CREATE UNIQUE INDEX idx_wditems_wid ON wditems (wiki_id);

CREATE TABLE viafs (
  id INTEGER PRIMARY KEY,
  viaf_id TEXT,
  human_id INTEGER,
  wiki_id TEXT
);

CREATE INDEX idx_viafs_viaf ON viafs (viaf_id);
CREATE INDEX idx_viafs_wiki ON viafs (wiki_id);
CREATE INDEX idx_viafs_human ON viafs (human_id);
```

You may use

```bash
/bin/restart
```

To start parsing

```bash
./bin/parse.py wikidata/split-0000.json.bz2
```

## DB 

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
  - [https://madflex.de/splitting-a-big-file-with-split] for splitting the big wikidata file

## TODO

  - [https://github.com/ijl/orjson]
  - ...
