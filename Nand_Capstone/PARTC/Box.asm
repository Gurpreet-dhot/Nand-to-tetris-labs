// ==============================================================================
// Box.asm - Capstone Project: Make the Computer Draw a Box
// Nand to Tetris - I (ETCCNT301) — School of Engineering & Technology, K.R. Mangalam University
//
// Student Name: Gurpreet Singh
// Roll Number:  2501410028
// Personal K:   28 (Last two digits of Roll Number)
//
// Box Specifications:
//   - Starting Row:     K = 28
//   - Height:           20 rows (Rows 28 to 47)
//   - Width in Words:   (K mod 4) + 1 = (28 % 4) + 1 = 1 words
//   - Width in Pixels:  16 * 1 = 16 pixels (from left edge)
//   - Base Address:     SCREEN + 32 * K = 16384 + 32 * 28 = 17280
//
// Behavior:
//   - Continuously polls Keyboard register (@KBD / RAM[24576]).
//   - When ANY key is pressed (RAM[KBD] != 0): Fills box area with -1 (Black / 0xFFFF).
//   - When NO key is pressed (RAM[KBD] == 0): Fills box area with 0 (White / Clear).
//
// 🎯 VIVA QUESTION (On-the-spot modification):
//   "How to move the box down?"
//   Answer: Increase the starting address @17280 at label START_DRAW.
//   Each screen row has 32 words.
//   - To move down by 1 row:  change 17280 to 17312 (17280 + 32).
//   - To move down by 5 rows: change 17280 to 17440 (17280 + 160).
//   - To move down by 10 rows: change 17280 to 17600 (17280 + 320).
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
    // Step 2: Set starting Screen address: SCREEN (16384) + 32 * K (896) = 17280
    @17280          // <-- START ADDRESS FOR ROW K=28 (Modify in viva to move box!)
    D=A
    @curr_addr
    M=D              // curr_addr = 17280

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

    // Initialize Column Counter for current row (1 words per row)
    @1               // <-- WIDTH IN WORDS = (K mod 4) + 1
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
