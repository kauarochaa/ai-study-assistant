"""Local history, with short lived SQLite connections."""
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


class History:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, created TEXT, question TEXT, answer TEXT, sources TEXT, mode TEXT)")

    def add(self, question, answer, sources, mode):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("INSERT INTO history(created,question,answer,sources,mode) VALUES(?,?,?,?,?)",
                       (datetime.now(timezone.utc).isoformat(), question, answer, json.dumps(sources, ensure_ascii=False), mode))

    def recent(self, limit=20):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [{**dict(row), "sources": json.loads(row["sources"])} for row in reversed(rows)]
