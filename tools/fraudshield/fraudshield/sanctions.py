"""OpenSanctions screening database (SQLite).

Data: https://www.opensanctions.org/datasets/default/ (targets.simple.csv).
Licence: CC BY-NC 4.0 for non-commercial use; commercial use needs a paid licence
(https://www.opensanctions.org/licensing/). Keep the downloaded data out of git.
"""
import csv
import re
import sqlite3
import sys
import unicodedata
import urllib.request
from . import Finding

URL = "https://data.opensanctions.org/datasets/latest/default/targets.simple.csv"


def norm(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return " ".join(sorted(re.findall(r"[a-z0-9]+", s)))  # order-insensitive


def download(dest, url=URL):
    urllib.request.urlretrieve(url, dest)
    return dest


def build(csv_path, db_path):
    csv.field_size_limit(sys.maxsize)
    db = sqlite3.connect(db_path)
    db.executescript("""DROP TABLE IF EXISTS entity; DROP TABLE IF EXISTS name;
      CREATE TABLE entity(id TEXT PRIMARY KEY, schema TEXT, name TEXT, countries TEXT,
        sanctions TEXT, dataset TEXT, last_seen TEXT);
      CREATE TABLE name(norm TEXT, id TEXT);""")
    with open(csv_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            db.execute("INSERT OR REPLACE INTO entity VALUES(?,?,?,?,?,?,?)",
                       (r["id"], r["schema"], r["name"], r.get("countries", ""),
                        r.get("sanctions", ""), r.get("dataset", ""), r.get("last_seen", "")))
            for n in [r["name"]] + [a for a in r.get("aliases", "").split(";") if a.strip()]:
                db.execute("INSERT INTO name VALUES(?,?)", (norm(n), r["id"]))
    db.execute("CREATE INDEX idx_norm ON name(norm)")
    db.commit()
    return db.execute("SELECT count(*) FROM entity").fetchone()[0]


def screen(db_path, names):
    """Exact normalized-name match. Names collide: every hit needs human review."""
    db = sqlite3.connect(db_path)
    out = []
    for n in names:
        for (eid, name, ds, sanc) in db.execute(
                "SELECT e.id,e.name,e.dataset,e.sanctions FROM name n JOIN entity e ON e.id=n.id WHERE n.norm=?",
                (norm(n),)):
            out.append(Finding("sanctions.match", "high", f"'{n}' matches listed entity '{name}'",
                               {"queried": n, "entity_id": eid, "dataset": ds, "sanctions": sanc}))
    return out
