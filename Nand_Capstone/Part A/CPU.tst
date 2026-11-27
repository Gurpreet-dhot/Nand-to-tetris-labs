// This file is part of www.nand2tetris.org
// CPU.tst

load CPU.hdl,
output-file CPU.out,
compare-to CPU.cmp,
output-list time%S0.4.0 inM%D1.6.1 instruction%B1.16.1 reset%B2.1.2 outM%D1.6.1 writeM%B2.1.2 addressM%D0.5.2 pc%D0.5.2;

// Load constant 12345 into A-register
set inM 0,
set reset 0,
set instruction %B0011000000111001,
eval,
output;
tick,
tock,
output;

// D = A
set instruction %B1110110000010000,
eval,
output;
tick,
tock,
output;

// Load constant 23456 into A-register
set instruction %B0101101110100000,
eval,
output;
tick,
tock,
output;

// D = D - A
set instruction %B1110010011010000,
eval,
output;
tick,
tock,
output;

// Write D to M[A]
set instruction %B1110001100001000,
eval,
output;
tick,
tock,
output;

// Reset PC
set reset 1,
set instruction %B0000000000000000,
eval,
output;
tick,
tock,
output;
