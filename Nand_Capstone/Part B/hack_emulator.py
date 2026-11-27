#!/usr/bin/env python3
"""
hack_emulator.py - Hack Hardware & Screen Simulator in Python
Capstone Project: Make the Computer Draw a Box
Simulates the Hack CPU, Memory (RAM16K + Screen + Keyboard), and renders the Screen.
"""

import sys
import os

class HackCPU:
    def __init__(self):
        self.a = 0
        self.d = 0
        self.pc = 0

    def step(self, instruction: int, in_m: int) -> tuple[int, bool, int, int]:
        """
        Executes one clock cycle.
        Returns: (out_m, write_m, address_m, next_pc)
        """
        out_m = 0
        write_m = False
        address_m = self.a & 0x7FFF

        # A-instruction: 0vvv vvvv vvvv vvvv
        if (instruction & 0x8000) == 0:
            self.a = instruction & 0x7FFF
            self.pc = (self.pc + 1) & 0x7FFF
            return out_m, write_m, address_m, self.pc

        # C-instruction: 111a cccccc ddd jjj
        a_bit = (instruction >> 12) & 1
        comp_code = (instruction >> 6) & 0x3F
        dest_code = (instruction >> 3) & 7
        jump_code = instruction & 7

        y = in_m if a_bit else self.a

        # ALU computation
        zx = (comp_code >> 5) & 1
        nx = (comp_code >> 4) & 1
        zy = (comp_code >> 3) & 1
        ny = (comp_code >> 2) & 1
        f  = (comp_code >> 1) & 1
        no = comp_code & 1

        x = self.d
        if zx: x = 0
        if nx: x = (~x) & 0xFFFF
        if zy: y = 0
        if ny: y = (~y) & 0xFFFF

        alu_out = (x + y) & 0xFFFF if f else (x & y)
        if no: alu_out = (~alu_out) & 0xFFFF

        # Handle 16-bit signed interpretation
        alu_signed = alu_out if alu_out < 0x8000 else alu_out - 0x10000
        zr = 1 if alu_out == 0 else 0
        ng = 1 if alu_signed < 0 else 0
        pos = 1 if (not zr and not ng) else 0

        # Destinations: d1=A, d2=D, d3=M
        if dest_code & 1:  # M
            out_m = alu_out
            write_m = True
        if dest_code & 2:  # D
            self.d = alu_out
        if dest_code & 4:  # A
            self.a = alu_out & 0x7FFF

        # Jump logic: j1 (< 0), j2 (== 0), j3 (> 0)
        j1 = (jump_code >> 2) & 1
        j2 = (jump_code >> 1) & 1
        j3 = jump_code & 1
        should_jump = (j1 and ng) or (j2 and zr) or (j3 and pos)

        if should_jump:
            self.pc = self.a & 0x7FFF
        else:
            self.pc = (self.pc + 1) & 0x7FFF

        return out_m, write_m, self.a & 0x7FFF, self.pc


class HackComputer:
    def __init__(self, rom_instructions: list[int]):
        self.rom = rom_instructions + [0] * (32768 - len(rom_instructions))
        self.ram = [0] * 32768  # 0..16383: RAM, 16384..24575: Screen, 24576: Keyboard
        self.cpu = HackCPU()

    def set_key(self, key_code: int):
        self.ram[24576] = key_code

    def step(self):
        pc = self.cpu.pc
        inst = self.rom[pc] if pc < 32768 else 0
        addr_m = self.cpu.a & 0x7FFF
        in_m = self.ram[addr_m] if addr_m < 32768 else 0

        out_m, write_m, target_addr, next_pc = self.cpu.step(inst, in_m)
        if write_m and target_addr < 24576:  # KBD is read-only
            self.ram[target_addr] = out_m

    def run_cycles(self, cycles: int):
        for _ in range(cycles):
            self.step()

    def render_screen_ascii(self, start_row: int = 35, end_row: int = 65, width_words: int = 4) -> str:
        """Renders an ASCII snippet of the screen around the box."""
        lines = []
        lines.append(f"Row Range [{start_row} .. {end_row}], First {width_words * 16} pixels:")
        lines.append("Row |" + "".join(f" Word {w} " for w in range(width_words)))
        lines.append("-" * (6 + width_words * 8))

        for r in range(start_row, end_row + 1):
            row_words = []
            for w in range(width_words):
                addr = 16384 + r * 32 + w
                val = self.ram[addr]
                row_words.append(f" 0x{val:04X} ")
            has_black = any(self.ram[16384 + r * 32 + w] != 0 for w in range(width_words))
            tag = "  <-- BOX" if has_black else ""
            lines.append(f"{r:3d} |" + "".join(row_words) + tag)
        return "\n".join(lines)


def load_hack_file(hack_path: str) -> list[int]:
    instructions = []
    with open(hack_path, "r") as f:
        for line in f:
            clean = line.strip()
            if clean:
                instructions.append(int(clean, 2))
    return instructions


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hack_emulator.py <file.hack>")
        sys.exit(1)

    hack_file = sys.argv[1]
    rom = load_hack_file(hack_file)
    sim = HackComputer(rom)

    print(f"Loaded {len(rom)} instructions from {hack_file}.")

    # Test 1: No key pressed (KBD = 0)
    print("\n--- Phase 1: No Key Pressed (Screen should be clear) ---")
    sim.set_key(0)
    sim.run_cycles(3000)
    print(sim.render_screen_ascii(start_row=39, end_row=45, width_words=3))

    # Test 2: Key pressed (e.g. 'X' = 88)
    print("\n--- Phase 2: Key Pressed (RAM[24576] = 88, Box should appear) ---")
    sim.set_key(88)
    sim.run_cycles(3000)
    print(sim.render_screen_ascii(start_row=39, end_row=45, width_words=3))

    # Test 3: Key released (KBD = 0)
    print("\n--- Phase 3: Key Released (RAM[24576] = 0, Box should disappear) ---")
    sim.set_key(0)
    sim.run_cycles(3000)
    print(sim.render_screen_ascii(start_row=39, end_row=45, width_words=3))
