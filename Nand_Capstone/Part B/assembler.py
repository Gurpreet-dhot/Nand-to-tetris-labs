#!/usr/bin/env python3
"""
assembler.py - Hack Computer Assembler
Capstone Project: Make the Computer Draw a Box
Nand to Tetris - I (ETCCNT301) — School of Engineering & Technology, K.R. Mangalam University

Translates Hack assembly programs (.asm) into 16-bit binary machine code (.hack).

Features:
- Two-pass architecture (Pass 1: Label recording & validation; Pass 2: Code generation & Variable mapping).
- Full support for Hack predefined symbols (SP, LCL, ARG, THIS, THAT, R0-R15, SCREEN, KBD).
- Support for student-specific K parameter extra features:
    * K mod 3 == 0: Export all symbols and variables to symbols.txt
    * K mod 3 == 1: Clear line-numbered error diagnostics instead of crashing
    * K mod 3 == 2: Duplicate label detection and warning
"""

import sys
import os
import argparse
from typing import Dict, List, Tuple, Optional

# Predefined Symbols in the Hack Platform
PREDEFINED_SYMBOLS: Dict[str, int] = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}
for i in range(16):
    PREDEFINED_SYMBOLS[f"R{i}"] = i

# C-Instruction Destination (dest) Bit Table: d1 d2 d3
DEST_TABLE: Dict[str, str] = {
    None: "000",
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "DM": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
    "ADM": "111",
}

# C-Instruction Jump (jump) Bit Table: j1 j2 j3
JUMP_TABLE: Dict[str, str] = {
    None: "000",
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

# C-Instruction Computation (comp) Bit Table: a c1 c2 c3 c4 c5 c6
COMP_TABLE: Dict[str, str] = {
    # a = 0 (ALU operates on D and A)
    "0":   "0101010",
    "1":   "0111111",
    "-1":  "0111010",
    "D":   "0001100",
    "A":   "0110000",
    "!D":  "0001101",
    "!A":  "0110001",
    "-D":  "0001111",
    "-A":  "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "A+D": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "A&D": "0000000",
    "D|A": "0010101",
    "A|D": "0010101",

    # a = 1 (ALU operates on D and M)
    "M":   "1110000",
    "!M":  "1110001",
    "-M":  "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "M+D": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "M&D": "1000000",
    "D|M": "1010101",
    "M|D": "1010101",
}


class HackAssembler:
    """Two-Pass Hack Assembler with student K extra features."""

    def __init__(self, k_value: Optional[int] = None):
        self.k = k_value
        self.k_mod_3 = (k_value % 3) if k_value is not None else None
        self.symbol_table: Dict[str, int] = dict(PREDEFINED_SYMBOLS)
        self.user_symbols: Dict[str, int] = {}  # Labels and variables
        self.next_var_address: int = 16
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def clean_line(self, line: str) -> str:
        """Strip comments (//...) and surrounding whitespace."""
        comment_idx = line.find("//")
        if comment_idx != -1:
            line = line[:comment_idx]
        return line.strip()

    def first_pass(self, lines: List[str]) -> List[Tuple[int, str]]:
        """
        First pass:
        - Removes comments and blank lines.
        - Records labels (LABEL) mapped to next ROM instruction address.
        - Feature K mod 3 == 2: Warns if same label is declared more than once.
        - Returns list of (original_line_num, instruction_text).
        """
        cleaned_instructions: List[Tuple[int, str]] = []
        rom_address = 0
        seen_labels: Dict[str, int] = {}

        for line_num, raw_line in enumerate(lines, start=1):
            cleaned = self.clean_line(raw_line)
            if not cleaned:
                continue

            # Check if this line is a pseudo-instruction label: (LABEL)
            if cleaned.startswith("(") and cleaned.endswith(")"):
                label_name = cleaned[1:-1].strip()
                if not label_name:
                    self.errors.append(f"Line {line_num}: Empty label definition '()'")
                    continue

                # K mod 3 == 2 feature: check duplicate labels
                if label_name in seen_labels:
                    msg = (
                        f"Warning: Duplicate label '({label_name})' at Line {line_num} "
                        f"(previously defined at Line {seen_labels[label_name]})"
                    )
                    self.warnings.append(msg)
                    print(f"⚠️  {msg}")
                else:
                    seen_labels[label_name] = line_num

                # Add label to symbol table pointing to the upcoming ROM address
                self.symbol_table[label_name] = rom_address
                self.user_symbols[label_name] = rom_address
            else:
                # Normal instruction (A- or C-instruction)
                cleaned_instructions.append((line_num, cleaned))
                rom_address += 1

        return cleaned_instructions

    def translate_a_instruction(self, line_num: int, inst: str) -> Optional[str]:
        """Translates @value or @symbol to 16-bit binary."""
        val_str = inst[1:].strip()
        if not val_str:
            self.errors.append(f"Line {line_num}: invalid instruction '{inst}' (missing value after '@')")
            return None

        # Check if constant decimal integer
        if val_str.isdigit():
            val = int(val_str)
            if val > 32767:
                self.errors.append(f"Line {line_num}: integer '{val}' exceeds 15-bit address limit (0-32767)")
                return None
            return f"{val:016b}"

        # Otherwise it is a symbol
        if val_str not in self.symbol_table:
            # New variable: assign next RAM address starting from 16
            self.symbol_table[val_str] = self.next_var_address
            self.user_symbols[val_str] = self.next_var_address
            self.next_var_address += 1

        val = self.symbol_table[val_str]
        return f"{val:016b}"

    def translate_c_instruction(self, line_num: int, inst: str) -> Optional[str]:
        """Translates dest=comp;jump into 16-bit binary: 111 a c1..c6 d1..d3 j1..j3."""
        # Parse dest
        if "=" in inst:
            dest_part, rest = inst.split("=", 1)
            dest_part = dest_part.strip()
        else:
            dest_part = ""
            rest = inst

        # Parse jump
        if ";" in rest:
            comp_part, jump_part = rest.split(";", 1)
            comp_part = comp_part.strip()
            jump_part = jump_part.strip()
        else:
            comp_part = rest.strip()
            jump_part = ""

        # Validate parts
        if dest_part not in DEST_TABLE:
            self.errors.append(f"Line {line_num}: invalid dest field '{dest_part}' in instruction '{inst}'")
            return None

        if comp_part not in COMP_TABLE:
            self.errors.append(f"Line {line_num}: invalid comp field '{comp_part}' in instruction '{inst}'")
            return None

        if jump_part not in JUMP_TABLE:
            self.errors.append(f"Line {line_num}: invalid jump field '{jump_part}' in instruction '{inst}'")
            return None

        comp_bits = COMP_TABLE[comp_part]
        dest_bits = DEST_TABLE[dest_part]
        jump_bits = JUMP_TABLE[jump_part]

        return f"111{comp_bits}{dest_bits}{jump_bits}"

    def second_pass(self, instructions: List[Tuple[int, str]]) -> List[str]:
        """
        Second pass:
        - Translates each line into 16-bit binary.
        - Feature K mod 3 == 1: Catches syntax errors with line numbers.
        """
        machine_code: List[str] = []

        for line_num, inst in instructions:
            if inst.startswith("@"):
                bin_code = self.translate_a_instruction(line_num, inst)
            else:
                bin_code = self.translate_c_instruction(line_num, inst)

            if bin_code is not None:
                machine_code.append(bin_code)

        return machine_code

    def save_symbols_file(self, output_path: str = "symbols.txt"):
        """Feature K mod 3 == 0: Save all labels and variables with their addresses."""
        with open(output_path, "w") as f:
            f.write("# Hack Assembler Symbol Table (Labels & Variables)\n")
            f.write(f"# Generated for Capstone Project (K={self.k})\n")
            f.write(f"{'SYMBOL':<20} {'DECIMAL':<10} {'HEX':<10}\n")
            f.write("-" * 42 + "\n")
            for sym, addr in sorted(self.user_symbols.items(), key=lambda x: (x[1], x[0])):
                f.write(f"{sym:<20} {addr:<10} 0x{addr:04X}\n")

    def assemble(self, asm_source: str) -> Optional[List[str]]:
        """Assembles source string into list of 16-bit binary strings."""
        lines = asm_source.splitlines()
        instructions = self.first_pass(lines)
        machine_code = self.second_pass(instructions)

        if self.errors:
            # K mod 3 == 1 feature: Clean diagnostics
            print("\n❌ Assembly Failed with Errors:")
            for err in self.errors:
                print(f"   {err}")
            return None

        return machine_code


def assemble_file(input_asm: str, output_hack: Optional[str] = None, k_val: Optional[int] = None) -> bool:
    """Utility function to assemble a .asm file into a .hack file."""
    if not os.path.exists(input_asm):
        print(f"Error: Input file '{input_asm}' does not exist.")
        return False

    if output_hack is None:
        base, _ = os.path.splitext(input_asm)
        output_hack = base + ".hack"

    with open(input_asm, "r") as f:
        source_code = f.read()

    print(f"==================================================")
    print(f" Hack Assembler (ETCCNT301 Capstone)")
    print(f" Input:  {input_asm}")
    print(f" Output: {output_hack}")
    if k_val is not None:
        mod = k_val % 3
        features = {
            0: "Save labels & variables in symbols.txt",
            1: "Informative error messages with line numbers",
            2: "Duplicate label detection & warnings"
        }
        print(f" Student K = {k_val} (K mod 3 = {mod} -> Feature: {features[mod]})")
    print(f"==================================================")

    assembler = HackAssembler(k_value=k_val)
    code = assembler.assemble(source_code)

    if code is None:
        return False

    with open(output_hack, "w") as f:
        for line in code:
            f.write(line + "\n")

    print(f"✅ Success! Assembled {len(code)} instructions into '{output_hack}'.")

    # Extra feature: symbols.txt (always save if K mod 3 == 0 or if user requested)
    symbols_dest = os.path.join(os.path.dirname(output_hack) or ".", "symbols.txt")
    assembler.save_symbols_file(symbols_dest)
    print(f"📄 Symbol table exported to '{symbols_dest}'.")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hack Computer Assembler (Nand to Tetris Capstone)")
    parser.add_argument("asm_file", help="Path to input .asm file")
    parser.add_argument("hack_file", nargs="?", default=None, help="Path to output .hack file (optional)")
    parser.add_argument("-k", "--k-val", type=int, default=28, help="Student K value (default: 28)")
    args = parser.parse_args()

    success = assemble_file(args.asm_file, args.hack_file, args.k_val)
    sys.exit(0 if success else 1)
