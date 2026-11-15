import json
import socket
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "olist.db"


@pytest.fixture(scope="session")
def db():
    if not DB.exists():
        pytest.fail("data/olist.db belum ada: jalankan scripts/get_data.sh lalu python scripts/build_db.py")
    con = sqlite3.connect(DB)
    yield con
    con.close()


@pytest.fixture(scope="session")
def q(db):
    def run(sql):
        return db.execute(sql).fetchall()
    return run


@pytest.fixture(scope="session")
def data():
    return json.loads((ROOT / "dashboard" / "data.json").read_text())


@pytest.fixture(scope="session")
def site():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "-d", str(ROOT / "dashboard")],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.1)
    yield f"http://127.0.0.1:{port}/"
    proc.terminate()
