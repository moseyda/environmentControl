// Static tests for Arduino sketch and header
// This file uses plain C++ and does not require Arduino runtime.
// It checks presence of expected symbols by parsing the source files at build time.

#include <fstream>
#include <sstream>
#include <string>
#include <iostream>

static std::string read_file(const char* path) {
    std::ifstream in(path);
    if (!in) return std::string();
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

int main() {
    const char* ino = "../sketch_dec26a.ino";
    const char* hdr = "../DHT.h";

    std::string s_ino = read_file(ino);
    std::string s_hdr = read_file(hdr);

    if (s_ino.empty()) {
        std::cerr << "ERROR: could not read " << ino << "\n";
        return 2;
    }
    if (s_hdr.empty()) {
        std::cerr << "ERROR: could not read " << hdr << "\n";
        return 2;
    }

    bool ok = true;

    // Check for setup() and loop()
    if (s_ino.find("void setup()") == std::string::npos) {
        std::cerr << "Missing setup() in sketch" << std::endl;
        ok = false;
    }
    if (s_ino.find("void loop()") == std::string::npos) {
        std::cerr << "Missing loop() in sketch" << std::endl;
        ok = false;
    }

    // Check for includes
    if (s_ino.find("#include <DHT.h>") == std::string::npos) {
        std::cerr << "Sketch does not include <DHT.h>" << std::endl;
        ok = false;
    }
    if (s_ino.find("#include <LiquidCrystal.h>") == std::string::npos) {
        std::cerr << "Sketch does not include <LiquidCrystal.h>" << std::endl;
        ok = false;
    }

    // Check header guard in DHT.h
    if (s_hdr.find("#ifndef DHT_H") == std::string::npos || s_hdr.find("#define DHT_H") == std::string::npos) {
        std::cerr << "DHT.h missing header guard DHT_H" << std::endl;
        ok = false;
    }

    // Check DHT class presence
    if (s_hdr.find("class DHT") == std::string::npos) {
        std::cerr << "DHT.h does not define class DHT" << std::endl;
        ok = false;
    }

    // Check for the DHT type macros/constants
    if (s_hdr.find("static const uint8_t DHT11") == std::string::npos) {
        std::cerr << "DHT11 constant missing in DHT.h" << std::endl;
        ok = false;
    }

    if (!ok) {
        std::cerr << "One or more static checks failed." << std::endl;
        return 1;
    }

    std::cout << "All static Arduino checks passed." << std::endl;
    return 0;
}
