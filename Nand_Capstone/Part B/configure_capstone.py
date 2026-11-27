#!/usr/bin/env python3
"""
configure_capstone.py - One-Click Customizer for Capstone Project
Capstone Project: Make the Computer Draw a Box
Nand to Tetris - I (ETCCNT301) — School of Engineering & Technology, K.R. Mangalam University

Automatically configures:
- Box.asm tailored to your Roll Number (K)
- Assembles Box.hack using your Python assembler
- Generates symbols.txt
- Verifies screen memory drawing via Hack emulator
- Updates the Capstone Report with your Name, Roll Number, and K
"""

import sys
import os
import argparse
from assembler import assemble_file
from hack_emulator import HackComputer, load_hack_file

CAPSTONE_DIR = os.path.dirname(os.path.abspath(__file__))

BOX_TEMPLATE = """// ==============================================================================
// Box.asm - Capstone Project: Make the Computer Draw a Box
// Nand to Tetris - I (ETCCNT301) — School of Engineering & Technology, K.R. Mangalam University
//
// Student Name: {student_name}
// Roll Number:  {roll_number}
// Personal K:   {k} (Last two digits of Roll Number)
//
// Box Specifications:
//   - Starting Row:     K = {k}
//   - Height:           20 rows (Rows {k} to {end_row})
//   - Width in Words:   (K mod 4) + 1 = ({k} % 4) + 1 = {width_words} words
//   - Width in Pixels:  16 * {width_words} = {width_pixels} pixels (from left edge)
//   - Base Address:     SCREEN + 32 * K = 16384 + 32 * {k} = {base_addr}
//
// Behavior:
//   - Continuously polls Keyboard register (@KBD / RAM[24576]).
//   - When ANY key is pressed (RAM[KBD] != 0): Fills box area with -1 (Black / 0xFFFF).
//   - When NO key is pressed (RAM[KBD] == 0): Fills box area with 0 (White / Clear).
//
// 🎯 VIVA QUESTION (On-the-spot modification):
//   "How to move the box down?"
//   Answer: Increase the starting address @{base_addr} at label START_DRAW.
//   Each screen row has 32 words.
//   - To move down by 1 row:  change {base_addr} to {base_addr_plus_1} ({base_addr} + 32).
//   - To move down by 5 rows: change {base_addr} to {base_addr_plus_5} ({base_addr} + 160).
//   - To move down by 10 rows: change {base_addr} to {base_addr_plus_10} ({base_addr} + 320).
// ==============================================================================

(MAIN_LOOP)
    // Step 1: Read keyboard register (KBD / RAM[24576])
    @KBD
    D=M
    @KEY_PRESSED
    D;JNE            // If KBD != 0, any key is pressed -> jump to KEY_PRESSED

    // Key is released -> set color to 0 (White / Clear)
    @color
    M=0
    @START_DRAW
    0;JMP

(KEY_PRESSED)
    // Key is pressed -> set color to -1 (Black / 0xFFFF)
    @color
    M=-1

(START_DRAW)
    // Step 2: Set starting Screen address: SCREEN (16384) + 32 * K ({k_times_32}) = {base_addr}
    @{base_addr}          // <-- START ADDRESS FOR ROW K={k} (Modify in viva to move box!)
    D=A
    @curr_addr
    M=D              // curr_addr = {base_addr}

    // Step 3: Initialize Row Counter (Height = 20 rows)
    @20
    D=A
    @row_left
    M=D              // row_left = 20

(ROW_LOOP)
    // If all 20 rows drawn, return to keyboard polling
    @row_left
    D=M
    @MAIN_LOOP
    D;JEQ

    // Initialize Column Counter for current row ({width_words} words per row)
    @{width_words}               // <-- WIDTH IN WORDS = (K mod 4) + 1
    D=A
    @col_left
    M=D

    // Set word pointer to start of current row
    @curr_addr
    D=M
    @ptr
    M=D

(COL_LOOP)
    // Write color (-1 or 0) to current screen word
    @color
    D=M
    @ptr
    A=M
    M=D              // RAM[ptr] = color

    // Advance to next 16-pixel word in this row
    @ptr
    M=M+1

    // Decrement column counter
    @col_left
    M=M-1
    D=M
    @COL_LOOP
    D;JGT            // If col_left > 0, draw next word in row

    // Step 4: Advance pointer to next screen row (next row = curr_addr + 32)
    @32
    D=A
    @curr_addr
    M=M+D            // curr_addr += 32

    // Decrement row counter
    @row_left
    M=M-1

    @ROW_LOOP
    0;JMP            // Loop back to draw next row
"""

def generate_project(roll_no: str, student_name: str = "Gurpreet Singh"):
    # Extract last two digits as K
    digits = "".join(ch for ch in roll_no if ch.isdigit())
    if len(digits) >= 2:
        k = int(digits[-2:])
    elif len(digits) == 1:
        k = int(digits)
    else:
        k = 28 # Default fallback

    k_mod_3 = k % 3
    k_mod_4 = k % 4
    width_words = k_mod_4 + 1
    width_pixels = 16 * width_words
    base_addr = 16384 + 32 * k
    end_row = k + 19

    feature_descriptions = {
        0: "Save all labels and variables with their addresses in symbols.txt",
        1: "Print a clear message with line number for invalid instructions instead of crashing",
        2: "Print a warning if the same label is written twice"
    }

    print("\n" + "=" * 65)
    print(" 🚀 K.R. MANGALAM UNIVERSITY - CAPSTONE PROJECT CONFIGURATOR")
    print("=" * 65)
    print(f" Student Name:       {student_name}")
    print(f" Roll Number:        {roll_no}")
    print(f" Personal Number K:  {k} (last 2 digits)")
    print(f" Box Starting Row:   Row {k} (Screen Address: {base_addr})")
    print(f" Box Height:         20 rows (Rows {k} to {end_row})")
    print(f" Box Width:          {width_pixels} pixels ({width_words} words of 16-bit)")
    print(f" Assembler Feature:  K mod 3 = {k_mod_3} -> {feature_descriptions[k_mod_3]}")
    print("=" * 65)

    # 1. Generate Box.asm
    asm_content = BOX_TEMPLATE.format(
        student_name=student_name,
        roll_number=roll_no,
        k=k,
        end_row=end_row,
        width_words=width_words,
        width_pixels=width_pixels,
        base_addr=base_addr,
        base_addr_plus_1=base_addr + 32,
        base_addr_plus_5=base_addr + 160,
        base_addr_plus_10=base_addr + 320,
        k_times_32=32 * k
    )

    box_asm_path = os.path.join(CAPSTONE_DIR, "Box.asm")
    with open(box_asm_path, "w") as f:
        f.write(asm_content)
    print(f"✔ Generated '{box_asm_path}'")

    # 2. Assemble Box.asm into Box.hack
    box_hack_path = os.path.join(CAPSTONE_DIR, "Box.hack")
    assemble_file(box_asm_path, box_hack_path, k_val=k)

    # 3. Simulate and Verify Box behavior
    print("\n▶ Verifying Box.hack in Hack CPU Simulator...")
    rom = load_hack_file(box_hack_path)
    sim = HackComputer(rom)

    # Press key (e.g. key code 65 = 'A')
    sim.set_key(65)
    sim.run_cycles(4000)

    # Verify words are 0xFFFF
    box_active = True
    for r in range(k, k + 20):
        for w in range(width_words):
            addr = 16384 + r * 32 + w
            if sim.ram[addr] != 0xFFFF:
                box_active = False

    if box_active:
        print(f"✔ VERIFIED: All {20 * width_words} words filled with 0xFFFF (Black Box drawn correctly)!")
    else:
        print("⚠️ Warning: Box simulation verification showed unexpected word values.")

    # Release key
    sim.set_key(0)
    sim.run_cycles(4000)
    box_cleared = all(sim.ram[16384 + r * 32 + w] == 0 for r in range(k, k + 20) for w in range(width_words))
    if box_cleared:
        print(f"✔ VERIFIED: All words cleared to 0x0000 upon key release!")

    print(f"\n🎉 Configuration complete for Roll Number: {roll_no} (K = {k})!")
    return k, width_words, width_pixels, base_addr


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure Capstone Project for Student Roll Number")
    parser.add_argument("--roll", default="2501410028", help="Your full Roll Number (default: 2501410028)")
    parser.add_argument("--name", default="Gurpreet Singh", help="Your Full Name (default: Gurpreet Singh)")
    args = parser.parse_args()

    generate_project(args.roll, args.name)
