# Capstone Project: Make the Computer Draw a Box
**Nand to Tetris – I (ETCCNT301) — School of Engineering & Technology, K.R. Mangalam University**  
**Student:** Gurpreet Singh  
**Roll No:** 2501410028 *(Configure with your roll number using python configure_capstone.py)*  

---

## 🚀 Quick Start (Ek Click Me Sab Chalao)

### 1. Apna Roll Number Set Karna:
Agar aapka roll number different hai, toh terminal me bas yeh command run karein:
```bash
python3 configure_capstone.py --roll <APNA_ROLL_NO> --name "Gurpreet Singh"
```
Yeh script automatically:
1. Aapka **K** (last two digits) calculate karega.
2. `Box.asm` ko aapke K ke starting row aur width ke hisaab se update karega.
3. Aapke custom `assembler.py` se compile karke `Box.hack` generate karega.
4. `symbols.txt` export karega.
5. Verification emulator run karke verify karega.

---

### 2. Mam Ko Interactive Demo Dikhana (Super Attractive!):
Folder me `index.html` file hai. Isko double-click karke kisi bhi browser (Chrome / Safari / Edge) me open karein:
- **Live Screen Display:** 512×256 Hack display dikhega.
- **Interactive Keyboard:** Keyboard par koi bhi button press karein ya button hold karein -> Row K par exact width ka black box instantly appear ho jayega!
- Button release karte hi box gayab ho jayega!
- Tabs me **CPU internal registers**, **Viva cheat sheet**, aur **Assembly source** live dikhega!
Mam dekh kar 100% impress hongi!

---

### 3. Assembler Test Run Karna:
Sare benchmark programs (Add, Max, Rect) aur aapke K features ko verify karne ke liye:
```bash
python3 verify_assembler.py
```
Sabhi tests automatically pass honge bit-for-bit!

---

### 4. Box.asm Assemble Karna:
```bash
python3 assembler.py Box.asm -k 28
```
Output: `Box.hack` aur `symbols.txt` create ho jayenge.

---

### 5. Official Hardware Simulator / CPU Emulator me Chana:
Aap official Nand2Tetris tools me bhi direct open kar sakte hain:
- **Hardware Simulator:** Load `CPU.tst`, `Memory.tst`, `ComputerAdd.tst`.
- **CPU Emulator:** Load `Box.hack` (ya `Box.asm`), set animation to "No Animation" or "Fast", click **Run**, aur emulator keyboard icon par click karke koi bhi key press karein!

---

## 🎯 Viva Spot Modification (5 Minutes Viva)
Mam bol sakti hain: *"Box ko thoda neeche karke dikhao!"*
- `Box.asm` open karein.
- Line 42 par jayein jahan `@17280` likha hai.
- Is number ko increase kar dein:
  - 1 row neeche karne ke liye: `17280 + 32 = 17312`
  - 10 rows neeche karne ke liye: `17280 + 320 = 17600`
- Terminal me run karein:
  ```bash
  python3 assembler.py Box.asm
  ```
- CPU Emulator me reload karke dikha dein!

---

## 📁 Files Included:
- `CPU.hdl` : Complete Hack CPU implementation
- `Memory.hdl` : Complete Memory map (RAM16K + Screen + Keyboard)
- `Computer.hdl` : Complete top-level Hack Computer
- `assembler.py` : Two-pass Python assembler with K mod 3 features
- `Box.asm` : Interactive box program in Hack assembly
- `Box.hack` : Binary machine code
- `symbols.txt` : Mapped symbols and memory addresses
- `index.html` : Interactive browser-based emulator and UI
- `REPORT.md` : 3-4 page short report ready to submit on ZOSIMA
- `verify_assembler.py` : Automated test suite
- `hack_emulator.py` : Python CPU simulator
- `configure_capstone.py` : One-click project generator for any roll number
