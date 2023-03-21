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


