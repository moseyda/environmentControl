from pathlib import Path
import re

SKETCH_FILE = Path(__file__).resolve().parents[1] / 'sketch_dec26a.ino'
DHT_FILE = Path(__file__).resolve().parents[1] / 'DHT.h'


def test_sketch_has_setup_and_loop():
    text = SKETCH_FILE.read_text(encoding='utf-8')
    assert re.search(r'\bvoid\s+setup\s*\(', text), 'setup() not found in sketch'
    assert re.search(r'\bvoid\s+loop\s*\(', text), 'loop() not found in sketch'


def test_sketch_includes_dht_header():
    text = SKETCH_FILE.read_text(encoding='utf-8')
    assert ('#include "DHT.h"' in text) or ('#include <DHT.h>' in text), 'DHT.h not included in sketch'


def test_dht_header_guard_and_contents():
    text = DHT_FILE.read_text(encoding='utf-8')
    # Header guard
    assert re.search(r'#ifndef\s+\w+', text), 'No #ifndef header guard in DHT.h'
    assert re.search(r'#define\s+\w+', text), 'No #define header guard in DHT.h'
    assert re.search(r'#endif', text), 'No #endif in DHT.h'
    # Some DHT-related symbol or class
    assert ('class DHT' in text) or ('DHT(' in text) or ('#define DHT' in text) or ('read' in text), 'DHT.h seems to lack DHT-related content'
