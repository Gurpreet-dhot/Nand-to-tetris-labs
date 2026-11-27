// Memory.tst
load Memory.hdl,
output-file Memory.out,
compare-to Memory.cmp,
output-list time%S0.4.0 in%D1.6.1 load%B2.1.2 address%D0.5.2 out%D1.6.1;

// Write into RAM16K[0]
set in 1111,
set load 1,
set address 0,
tick,
tock,
output;

// Read RAM16K[0]
set load 0,
eval,
output;

// Write into RAM16K[100]
set in 2222,
set load 1,
set address 100,
tick,
tock,
output;

// Read RAM16K[100]
set load 0,
eval,
output;

// Write into Screen[0] (Address 16384)
set in -1,
set load 1,
set address 16384,
tick,
tock,
output;

// Read Screen[0]
set load 0,
eval,
output;
