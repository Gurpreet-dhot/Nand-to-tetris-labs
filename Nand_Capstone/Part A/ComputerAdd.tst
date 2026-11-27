// ComputerAdd.tst
load Computer.hdl,
output-file ComputerAdd.out,
compare-to ComputerAdd.cmp,
output-list time%S0.4.0 reset%B2.1.2 ARegister[]%D1.6.1 DRegister[]%D1.6.1 pc[]%D0.5.2 RAM16K[0]%D1.6.1;

// Load Add.hack into ROM32K
ROM32K load tests/Add.hack,

// Reset computer
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
