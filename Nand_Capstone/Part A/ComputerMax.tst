// ComputerMax.tst
load Computer.hdl,
output-file ComputerMax.out,
compare-to ComputerMax.cmp,
output-list time%S0.4.0 reset%B2.1.2 pc[]%D0.5.2 RAM16K[0]%D1.6.1 RAM16K[1]%D1.6.1 RAM16K[2]%D1.6.1;

// Load Max.hack
ROM32K load tests/Max.hack,

// Set RAM[0] = 3, RAM[1] = 5 -> Max should be 5 in RAM[2]
set RAM16K[0] 3,
set RAM16K[1] 5,
set reset 1,
tick,
tock,
output;

set reset 0,
repeat 14 {
    tick,
    tock,
    output;
}
