import importlib.util
import sys
import types
import sqlite3
from pathlib import Path

class DummySerial:
    def __init__(self, *a, **k):
        pass
    def readline(self):
        return b''


def load_app_module():
    """Dynamically load `app.py` while patching `serial` and `time.sleep` to avoid hardware delays."""
    # Ensure a fake serial module exists so importing app.py won't try to open COM ports
    serial_mod = types.ModuleType('serial')
    serial_mod.Serial = lambda *a, **k: DummySerial()
    sys.modules['serial'] = serial_mod

    # Patch time.sleep to a no-op to avoid 2s delay at import
    import time
    time.sleep = lambda s: None

    # Load the module from file location
    file_path = Path(__file__).resolve().parents[1] / 'app.py'
    spec = importlib.util.spec_from_file_location('app_under_test', str(file_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extract_value_valid():
    module = load_app_module()
    assert module.extract_value('Temp: 23.5 Humidity: 45.2 Air Quality: 12.0', 'Temp') == 23.5
    assert module.extract_value('Humidity: 45', 'Humidity') == 45.0


def test_extract_value_invalid_and_missing():
    module = load_app_module()
    # Non-numeric value
    assert module.extract_value('Temp: abc', 'Temp') is None
    # Missing value
    assert module.extract_value('No temp here', 'Temp') is None


def test_database_insert_and_retrieve(tmp_path):
    module = load_app_module()
    db_path = tmp_path / 'test_env.db'
    # Use a temporary database for isolation
    module.DATABASE = str(db_path)
    module.create_table()
    module.insert_data(1.1, 2.2, 3.3)

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute('SELECT temperature, humidity, airQuality FROM data')
    rows = c.fetchall()
    conn.close()

    assert len(rows) == 1
    assert rows[0] == (1.1, 2.2, 3.3)


def test_get_db_connection(tmp_path):
    module = load_app_module()
    db_path = tmp_path / 'test_conn.db'
    module.DATABASE = str(db_path)
    conn = module.get_db_connection()
    assert conn is not None
    conn.close()
