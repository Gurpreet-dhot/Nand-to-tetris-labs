#!/usr/bin/env python3
"""
verify_assembler.py - Automated Verification Suite for Hack Assembler
Capstone Project: Make the Computer Draw a Box
Tests:
1. Bit-exact verification against standard reference files (Add, Max, Rect).
2. Feature K mod 3 == 0 (Symbols table generation).
3. Feature K mod 3 == 1 (Syntax error diagnostics with line numbers).
4. Feature K mod 3 == 2 (Duplicate label warnings).
"""

import os
import sys
from assembler import HackAssembler, assemble_file

TESTS_DIR = os.path.dirname(os.path.abspath(__file__)) + "/tests"

# Known official .hack reference outputs
EXPECTED_ADD_HACK = [
    "0000000000000010",
    "1110110000010000",
    "0000000000000011",
    "1110000010010000",
    "0000000000000000",
    "1110001100001000",
]

EXPECTED_MAX_HACK = [
    "0000000000000000",
    "1111110000010000",
    "0000000000000001",
    "1111010011010000",
    "0000000000001010",
    "1110001100000001",
    "0000000000000001",
    "1111110000010000",
    "0000000000001100",
    "1110101010000111",
    "0000000000000000",
    "1111110000010000",
    "0000000000000010",
    "1110001100001000",
    "0000000000001110",
    "1110101010000111",
]

EXPECTED_RECT_HACK = [
    "0000000000000000",
    "1111110000010000",
    "0000000000010111",
    "1110001100000110",
    "0000000000010000",
    "1110001100001000",
    "0100000000000000",
    "1110110000010000",
    "0000000000010001",
    "1110001100001000",
    "0000000000010001",
    "1111110000100000",
    "1110111010001000",
    "0000000000010001",
    "1111110000010000",
    "0000000000100000",
    "1110000010010000",
    "0000000000010001",
    "1110001100001000",
    "0000000000010000",
    "1111110010011000",
    "0000000000001010",
    "1110001100000001",
    "0000000000010111",
    "1110101010000111",
]

def test_bit_exactness():
    print("▶ Testing Assembler Bit-Exact Equivalence on Standard Programs...")

    # Test Add.asm
    asm = HackAssembler()
    with open(f"{TESTS_DIR}/Add.asm") as f:
        out = asm.assemble(f.read())
    assert out == EXPECTED_ADD_HACK, "Add.asm output mismatch!"
    print("  [PASS] Add.asm (100% bit-exact)")

    # Test Max.asm
    asm = HackAssembler()
    with open(f"{TESTS_DIR}/Max.asm") as f:
        out = asm.assemble(f.read())
    assert out == EXPECTED_MAX_HACK, "Max.asm output mismatch!"
    print("  [PASS] Max.asm (100% bit-exact)")

    # Test Rect.asm
    asm = HackAssembler()
    with open(f"{TESTS_DIR}/Rect.asm") as f:
        out = asm.assemble(f.read())
    assert out == EXPECTED_RECT_HACK, "Rect.asm output mismatch!"
    print("  [PASS] Rect.asm (100% bit-exact)")


def test_k_mod_features():
    print("\n▶ Testing Student Extra Features (K mod 3)...")

    # Feature 0: symbols.txt
    print("  Testing Feature 0 (K mod 3 == 0: symbols.txt export)...")
    asm0 = HackAssembler(k_value=42) # 42 % 3 == 0
    asm0.assemble("@myVar\nD=A\n(MY_LABEL)\n@myVar\nM=D\n")
    symbols_path = f"{TESTS_DIR}/test_symbols.txt"
    asm0.save_symbols_file(symbols_path)
    assert os.path.exists(symbols_path), "symbols.txt was not created!"
    with open(symbols_path) as f:
        content = f.read()
    assert "myVar" in content and "MY_LABEL" in content, "Symbols missing from symbols.txt"
    print("  [PASS] Feature 0: symbols.txt generated successfully")

    # Feature 1: Line number errors
    print("  Testing Feature 1 (K mod 3 == 1: Syntax error line reporting)...")
    asm1 = HackAssembler(k_value=43) # 43 % 3 == 1
    err_source = "@10\nD=A\nINVALID_INSTRUCTION_HERE\n@20\n"
    res1 = asm1.assemble(err_source)
    assert res1 is None, "Assembler should have failed on invalid syntax"
    assert any("Line 3" in err for err in asm1.errors), f"Expected 'Line 3' error, got: {asm1.errors}"
    print(f"  [PASS] Feature 1: Clear error diagnosed correctly -> {asm1.errors[0]}")

    # Feature 2: Duplicate label warning
    print("  Testing Feature 2 (K mod 3 == 2: Duplicate label warning)...")
    asm2 = HackAssembler(k_value=41) # 41 % 3 == 2
    dup_source = "(LOOP)\n@10\nD=A\n(LOOP)\n@LOOP\n0;JMP\n"
    res2 = asm2.assemble(dup_source)
    assert len(asm2.warnings) > 0, "Expected duplicate label warning"
    assert "Duplicate label '(LOOP)' at Line 4" in asm2.warnings[0], f"Unexpected warning: {asm2.warnings}"
    print(f"  [PASS] Feature 2: Warning triggered correctly -> {asm2.warnings[0]}")


if __name__ == "__main__":
    test_bit_exactness()
    test_k_mod_features()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! Assembler is 100% compliant.")
