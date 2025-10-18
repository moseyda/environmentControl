# environmentControl

Small environment monitoring project that contains two parts:

- `pythonProject1/` — a FastAPI-based backend that reads sensor data from a serial port (Arduino), stores it in an SQLite database and serves a simple dashboard and a WebSocket endpoint.
- `sketch_dec26a/` — Arduino sketch and DHT sensor header used on the microcontroller side. Contains static tests (Python and a C++ test utility).

This README explains how to set up the dev environment, run the services locally, and run the tests.

## Repository layout

```
pythonProject1/
  app.py                 # FastAPI app, DB helpers and serial reader
  tests/
    test_app.py          # pytest tests for the Python app

sketch_dec26a/
  DHT.h                  # DHT sensor header
  sketch_dec26a.ino      # Arduino sketch
  tests/
    test_sketch.py       # pytest static checks for sketch/header
    test_sketch.cpp      # optional C++ static-check utility (requires g++)
```

## Prerequisites

- Windows with PowerShell (instructions use PowerShell syntax)
- Python 3.8+ installed (your environment shows Python 3.12 available)
- pip
- (optional) a C++ compiler (g++ / MinGW-w64) if you want to compile and run the C++ static test in `sketch_dec26a/tests`.
- (optional) Arduino IDE or Arduino CLI to flash the sketch to a board.

Python packages used by the Python project (install below):
- fastapi
- uvicorn
- pyserial (if you intend to connect to a real Arduino)
- pytest (for running tests)

## Setup (Python)

Open PowerShell and create a virtual environment, then install the minimal dependencies:

```powershell
cd C:\<Users>\<user>\<yourHoldingFolder>\environmentControl\pythonProject1
python -m venv .venv
. .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
# install from requirements.txt (recommended)
cd ..
pip install -r requirements.txt
```

Notes:
- `app.py` opens a serial connection on `COM3` by default. If your Arduino is on a different port, edit `pythonProject1/app.py` and change the `arduino = serial.Serial(port='COM3', ...)` line to the correct port, or mock the serial during tests.
- The backend uses an SQLite database file `environment_data.db` in `pythonProject1/`.

## Run the FastAPI app locally

From the `pythonProject1` folder with the virtual environment activated:

```powershell
cd C:\<Users>\<user>\<yourHoldingFolder>\environmentControl\pythonProject1
# run the app (adjust host/port as needed)
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/` in a browser to see the dashboard HTML served by the app, or connect to the WebSocket at `ws://localhost:8000/ws` for live updates.

## Tests

Python (pytest)

From the repo root you can run all Python-based tests (this includes `pythonProject1/tests/test_app.py` and the Arduino static tests written in Python):

```powershell
cd C:\<Users>\<user>\<yourHoldingFolder>\environmentControl
# run all tests
python -m pytest -q
```

Or run tests per subproject:

```powershell
# Python backend tests only
cd pythonProject1
python -m pytest -q

# Arduino Python static checks only
cd ..\sketch_dec26a
python -m pytest tests/test_sketch.py -q
```

C++ static test (optional)

There is a small C++ program at `sketch_dec26a/tests/test_sketch.cpp` that reads the `.ino` and `DHT.h` files and performs the same static checks. This requires a C++ toolchain (g++). Example using g++ (PowerShell):

```powershell
cd C:\<Users>\<user>\<yourHoldingFile>\environmentControl\sketch_dec26a\tests
g++ -std=c++11 -O2 -Wall -o test_sketch.exe test_sketch.cpp
.\test_sketch.exe
```

If `g++` is not installed on your system you can install MinGW-w64 or MSYS2 and add the bin folder to your PATH. Alternatively the Python-based static tests work without a compiler.

## Notes and troubleshooting

- Serial port: `app.py` will attempt to open a serial port at startup. If you don't have an Arduino attached, tests may fail if they import code that opens the serial port on import. The current test suite is written to avoid starting long-running serial reads — if you see tests attempting to access COM ports, mock `serial.Serial` or set the port variable to a non-existent device for tests.
- Database file: the SQLite DB `environment_data.db` will be created automatically when `app.py` runs. Tests that manipulate the DB may create temporary rows — remove or inspect the file if needed.
- Arduino sketch: to flash the sketch, use Arduino IDE or `arduino-cli` and select the correct board & port.

## CI suggestions

- Run Python tests on every push using GitHub Actions with a Windows or Linux runner that installs Python and runs `pytest`.
- If you want to run the C++ test in CI, use a runner that includes a C++ toolchain (Ubuntu runners already include g++).

## Quick summary

- Python backend: `pythonProject1/app.py` (FastAPI + SQLite + serial)
- Arduino side: `sketch_dec26a/sketch_dec26a.ino` + `DHT.h`
- Tests:
  - Python tests: run `python -m pytest` from the repo root
  - Optional C++ static test: compile with `g++` and run `test_sketch.exe`


