# instructions.py
# Zoptymalizowana i KOMPLETNA mapa mikrokodu dla MOS 8501/8502 (PLUS/4).
# Wersja TURBO: Agresywny pipelining (Max 8 cykli dla instrukcji RMW).

# ==============================================================================
#  SEKCJA 1: MAKRA CYKLI I ADRESOWANIA
# ==============================================================================
FETCH = ["IR := *PC; PC += 1"]

# --- Generatory Cykli Adresowych (Zoptymalizowane) ---
# Cel: Zejść z liczbą cykli tak nisko, jak pozwala hardware (D-FlipFlop pipelining)

def c_imm():
    return ["DL := *PC; PC += 1"]

def c_zp():
    return ["DL := *PC; PC += 1", "ADL := DL"]

def c_zp_x():
    # Fetch Base -> Latch Base -> Add Index
    return ["DL := *PC; PC += 1", "ADL := DL", "DL := *{zeropage} + X; ADL := DL"]

def c_zp_y():
    return ["DL := *PC; PC += 1", "ADL := DL", "DL := *{zeropage} + Y; ADL := DL"]

def c_abs():
    # OPTYMALIZACJA: 3 cykle zamiast 4.
    # T1: Pobierz LSB.
    # T2: Zatrzask LSB w ADL ORAZ Pobranie MSB do DL (w jednym takcie).
    # T3: Zatrzask MSB w ADH.
    return [
        "DL := *PC; PC += 1",
        "ADL := DL; DL := *PC; PC += 1",
        "ADH := DL"
    ]

def c_abs_x_read():
    # 3 cykle adresowania. X dodawany sprzętowo przy odczycie.
    return [
        "DL := *PC; PC += 1",
        "ADL := DL; DL := *PC; PC += 1",
        "ADH := DL"
    ]

def c_abs_y_read():
    return [
        "DL := *PC; PC += 1",
        "ADL := DL; DL := *PC; PC += 1",
        "ADH := DL"
    ]

def c_ind_x():
    # OPTYMALIZACJA: 4 cykle zamiast 6.
    # T2: Sprzętowy sumator liczy wskaźnik, od razu czytamy LSB adresu.
    return [
        "DL := *PC; PC += 1",                                           # T1
        "ADL := {calculate_zp_x_pointer}; DL := *{zeropage_indirect}",  # T2
        "TMP := DL; DL := *{zeropage_indirect_inc}",                    # T3
        "ADH := DL; ADL := TMP"                                         # T4
    ]

def c_ind_y_read():
    # OPTYMALIZACJA: 4 cykle zamiast 6.
    return [
        "DL := *PC; PC += 1",                                           # T1
        "ADL := DL; DL := *{zeropage_indirect}",                        # T2
        "TMP := DL; DL := *{zeropage_indirect_inc}",                    # T3
        "ADH := DL; ADL := TMP"                                         # T4
    ]

def c_branch():
    return ["ADL := *PC; PC += 1; TEST_BRANCH_EN; END", "PC := {pc_plus_offset}; END"]

# ==============================================================================
#  SEKCJA 2: HELPERY OPERACJI
# ==============================================================================

def _get_read_src(cycles_addr):
    """Zwraca źródło odczytu pamięci."""
    if cycles_addr == c_zp(): return "*{zeropage}"
    if cycles_addr == c_zp_x(): return "*{zeropage}"
    if cycles_addr == c_zp_y(): return "*{zeropage}"
    if cycles_addr == c_abs_x_read(): return "*{latch} + X"
    if cycles_addr == c_abs_y_read(): return "*{latch} + Y"
    if cycles_addr == c_ind_y_read(): return "*{latch} + Y"
    # Domyślne
    return "*{latch}"

def op_read_alu(cycles_addr, alu_op, dest_reg):
    """Odczyt -> ALU -> Rejestr."""
    src = _get_read_src(cycles_addr)

    # Imm ma specjalną ścieżkę (krótszą)
    if cycles_addr == c_imm():
        return FETCH + cycles_addr + [f"{alu_op}({dest_reg}, DL); {dest_reg} := ALU_RESULT; ALU_FLAGS_LD; END"]

    # Standard: Adresowanie -> Odczyt do DL -> Execute
    return FETCH + cycles_addr + [f"DL := {src}; {alu_op}({dest_reg}, DL); {dest_reg} := ALU_RESULT; ALU_FLAGS_LD; END"]

def op_store(cycles_addr, src_reg):
    """Zapis rejestru."""
    target = _get_read_src(cycles_addr) # Target jest taki sam jak source
    return FETCH + cycles_addr + [f"{target} := {src_reg}; END"]

def op_rmw(cycles_addr, alu_op):
    """
    Legal RMW (INC, DEC...).
    Używa równoległego ładowania TMP := Mem, aby uniknąć problemów z opóźnieniem.
    """
    src = _get_read_src(cycles_addr)

    return FETCH + cycles_addr + [
        f"DL := {src}; TMP := {src}",       # Read Mem -> DL & TMP (Parallel)
        f"{alu_op}(TMP)",                   # Modify (TMP stable input) -> Result in ALU Latch?
        f"{src} := ALU_RESULT; ALU_FLAGS_LD; END" # Write Result
    ]

def op_bit(cycles_addr):
    src = _get_read_src(cycles_addr)
    return FETCH + cycles_addr + [f"DL := {src}; BIT(A, DL); ALU_FLAGS_LD; END"]

def op_sax(cycles_addr):
    """SAX (Store A AND X)."""
    target = _get_read_src(cycles_addr)
    return FETCH + cycles_addr + [
        "TMP := X; AND(A, TMP)",
        f"{target} := ALU_RESULT; END"
    ]

def op_complex_rmw(cycles_addr, rmw_op, alu_op):
    """
    Illegal RMW (SLO, ISC, DCP...).
    Klucz do 8 cykli: Równoległy odczyt (DL/TMP) i sklejona operacja zapisu/ALU.
    """
    src = _get_read_src(cycles_addr)

    return FETCH + cycles_addr + [
        # T6 (lub wcześniej): Odczyt do DL i TMP
        f"DL := {src}; TMP := {src}",

        # T7: Modyfikacja RMW.
        # TMP wystawia dane. ALU liczy. Wynik zapisujemy do RAM i do DL.
        f"{rmw_op}(TMP); {src} := ALU_RESULT; DL := ALU_RESULT",

        # T8: Operacja końcowa z A.
        # DL wystawia wynik RMW. ALU liczy z A.
        f"{alu_op}(A, DL); A := ALU_RESULT; ALU_FLAGS_LD; END"
    ]

# ==============================================================================
#  SEKCJA 3: MAPA INSTRUKCJI
# ==============================================================================
MICROCODE_MAP = {
    # --- 1. SYSTEM ---
    0xEA: ("NOP", "Impl", FETCH + ["END"]),
    0x00: ("BRK", "Impl", ["IR := *PC", "*SP := PCH; SP -= 1", "*SP := PCL; SP -= 1", "*SP := P; SETF(B); SP -= 1", "DL := *fCPL", "ADL := DL", "DL := *fCPH", "ADH := DL; PC := {ADH, ADL}; SETF(I); END"]),
    0x18: ("CLC", "Impl", FETCH + ["CLRF(C); END"]),
    0x38: ("SEC", "Impl", FETCH + ["SETF(C); END"]),
    0x58: ("CLI", "Impl", FETCH + ["CLRF(I); END"]),
    0x78: ("SEI", "Impl", FETCH + ["SETF(I); END"]),
    0xB8: ("CLV", "Impl", FETCH + ["CLRF(V); END"]),
    0xD8: ("CLD", "Impl", FETCH + ["CLRF(D); END"]),
    0xF8: ("SED", "Impl", FETCH + ["SETF(D); END"]),

    # --- 2. SKOKI ---
    0x4C: ("JMP", "Abs", FETCH + ["DL := *PC; PC += 1; ADL := DL", "DL := *PC; PC += 1; ADH := DL", "PC := {ADH, ADL}; END"]),
    0x6C: ("JMP", "Ind", FETCH + ["DL := *PC; PC += 1; ADL := DL", "DL := *PC; PC += 1; ADH := DL", "DL := *{latch}; ADL := DL", "DL := *{latch_inc}; ADH := DL", "PC := {ADH, ADL}; END"]),
    0x20: ("JSR", "Abs", FETCH + ["DL := *PC; PC += 1; ADL := DL", "*SP := PCH; SP -= 1", "*SP := PCL; SP -= 1", "DL := *PC; ADH := DL", "PC := {ADH, ADL}; END"]),
    0x60: ("RTS", "Impl", FETCH + ["SP += 1", "DL := *SP; PCL := DL", "SP += 1", "DL := *SP; PCH := DL", "PC += 1; END"]),
    0x40: ("RTI", "Impl", FETCH + ["SP += 1", "DL := *SP; P := DL", "SP += 1", "DL := *SP; PCL := DL", "SP += 1", "DL := *SP; PCH := DL", "END"]),

    # Skoki warunkowe
    0x10: ("BPL", "Rel", FETCH + c_branch()),
    0x30: ("BMI", "Rel", FETCH + c_branch()),
    0x50: ("BVC", "Rel", FETCH + c_branch()),
    0x70: ("BVS", "Rel", FETCH + c_branch()),
    0x90: ("BCC", "Rel", FETCH + c_branch()),
    0xB0: ("BCS", "Rel", FETCH + c_branch()),
    0xD0: ("BNE", "Rel", FETCH + c_branch()),
    0xF0: ("BEQ", "Rel", FETCH + c_branch()),

    # --- 3. TRANSFERY ---
    0xAA: ("TAX", "Impl", FETCH + ["PASS(A); X := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0xA8: ("TAY", "Impl", FETCH + ["PASS(A); Y := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x8A: ("TXA", "Impl", FETCH + ["PASS(X); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x98: ("TYA", "Impl", FETCH + ["PASS(Y); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0xBA: ("TSX", "Impl", FETCH + ["PASS(SP); X := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x9A: ("TXS", "Impl", FETCH + ["SP := X; END"]),

    # --- 4. STOS ---
    0x48: ("PHA", "Impl", FETCH + ["*SP := A; SP -= 1; END"]),
    0x08: ("PHP", "Impl", FETCH + ["*SP := P; SETF(B); SP -= 1; END"]),
    0x68: ("PLA", "Impl", FETCH + ["SP += 1", "DL := *SP", "A := DL; PASS(A); ALU_FLAGS_LD; END"]),
    0x28: ("PLP", "Impl", FETCH + ["SP += 1", "DL := *SP", "P := DL; END"]),

    # --- 5. LOAD/STORE ---
    0xA9: ("LDA", "#Imm",   FETCH + c_imm() + ["PASS(DL); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0xA5: ("LDA", "ZP",     op_read_alu(c_zp(), "PASS", "A")),
    0xB5: ("LDA", "ZP,X",   op_read_alu(c_zp_x(), "PASS", "A")),
    0xAD: ("LDA", "Abs",    op_read_alu(c_abs(), "PASS", "A")),
    0xBD: ("LDA", "Abs,X",  op_read_alu(c_abs_x_read(), "PASS", "A")),
    0xB9: ("LDA", "Abs,Y",  op_read_alu(c_abs_y_read(), "PASS", "A")),
    0xA1: ("LDA", "(ZP,X)", op_read_alu(c_ind_x(), "PASS", "A")),
    0xB1: ("LDA", "(ZP),Y", op_read_alu(c_ind_y_read(), "PASS", "A")),

    0xA2: ("LDX", "#Imm",   FETCH + c_imm() + ["PASS(DL); X := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0xA6: ("LDX", "ZP",     op_read_alu(c_zp(), "PASS", "X")),
    0xB6: ("LDX", "ZP,Y",   op_read_alu(c_zp_y(), "PASS", "X")),
    0xAE: ("LDX", "Abs",    op_read_alu(c_abs(), "PASS", "X")),
    0xBE: ("LDX", "Abs,Y",  op_read_alu(c_abs_y_read(), "PASS", "X")),

    0xA0: ("LDY", "#Imm",   FETCH + c_imm() + ["PASS(DL); Y := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0xA4: ("LDY", "ZP",     op_read_alu(c_zp(), "PASS", "Y")),
    0xB4: ("LDY", "ZP,X",   op_read_alu(c_zp_x(), "PASS", "Y")),
    0xAC: ("LDY", "Abs",    op_read_alu(c_abs(), "PASS", "Y")),
    0xBC: ("LDY", "Abs,X",  op_read_alu(c_abs_x_read(), "PASS", "Y")),

    0x85: ("STA", "ZP",     op_store(c_zp(), "A")),
    0x95: ("STA", "ZP,X",   op_store(c_zp_x(), "A")),
    0x8D: ("STA", "Abs",    op_store(c_abs(), "A")),
    0x9D: ("STA", "Abs,X",  op_store(c_abs_x_read(), "A")),
    0x99: ("STA", "Abs,Y",  op_store(c_abs_y_read(), "A")),
    0x81: ("STA", "(ZP,X)", op_store(c_ind_x(), "A")),
    0x91: ("STA", "(ZP),Y", op_store(c_ind_y_read(), "A")),

    0x86: ("STX", "ZP",     op_store(c_zp(), "X")),
    0x96: ("STX", "ZP,Y",   op_store(c_zp_y(), "X")),
    0x8E: ("STX", "Abs",    op_store(c_abs(), "X")),
    0x84: ("STY", "ZP",     op_store(c_zp(), "Y")),
    0x94: ("STY", "ZP,X",   op_store(c_zp_x(), "Y")),
    0x8C: ("STY", "Abs",    op_store(c_abs(), "Y")),

    # --- 6. ARYTMETYKA ---
    0x69: ("ADC", "#Imm",   FETCH + c_imm() + ["ADC(A, DL); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x65: ("ADC", "ZP",     op_read_alu(c_zp(), "ADC", "A")),
    0x75: ("ADC", "ZP,X",   op_read_alu(c_zp_x(), "ADC", "A")),
    0x6D: ("ADC", "Abs",    op_read_alu(c_abs(), "ADC", "A")),
    0x7D: ("ADC", "Abs,X",  op_read_alu(c_abs_x_read(), "ADC", "A")),
    0x79: ("ADC", "Abs,Y",  op_read_alu(c_abs_y_read(), "ADC", "A")),
    0x61: ("ADC", "(ZP,X)", op_read_alu(c_ind_x(), "ADC", "A")),
    0x71: ("ADC", "(ZP),Y", op_read_alu(c_ind_y_read(), "ADC", "A")),

    0xE9: ("SBC", "#Imm",   FETCH + c_imm() + ["SBC(A, DL); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0xE5: ("SBC", "ZP",     op_read_alu(c_zp(), "SBC", "A")),
    0xF5: ("SBC", "ZP,X",   op_read_alu(c_zp_x(), "SBC", "A")),
    0xED: ("SBC", "Abs",    op_read_alu(c_abs(), "SBC", "A")),
    0xFD: ("SBC", "Abs,X",  op_read_alu(c_abs_x_read(), "SBC", "A")),
    0xF9: ("SBC", "Abs,Y",  op_read_alu(c_abs_y_read(), "SBC", "A")),
    0xE1: ("SBC", "(ZP,X)", op_read_alu(c_ind_x(), "SBC", "A")),
    0xF1: ("SBC", "(ZP),Y", op_read_alu(c_ind_y_read(), "SBC", "A")),

    0x29: ("AND", "#Imm",   FETCH + c_imm() + ["AND(A, DL); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x25: ("AND", "ZP",     op_read_alu(c_zp(), "AND", "A")),
    0x35: ("AND", "ZP,X",   op_read_alu(c_zp_x(), "AND", "A")),
    0x2D: ("AND", "Abs",    op_read_alu(c_abs(), "AND", "A")),
    0x3D: ("AND", "Abs,X",  op_read_alu(c_abs_x_read(), "AND", "A")),
    0x39: ("AND", "Abs,Y",  op_read_alu(c_abs_y_read(), "AND", "A")),
    0x21: ("AND", "(ZP,X)", op_read_alu(c_ind_x(), "AND", "A")),
    0x31: ("AND", "(ZP),Y", op_read_alu(c_ind_y_read(), "AND", "A")),

    0x09: ("ORA", "#Imm",   FETCH + c_imm() + ["ORA(A, DL); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x05: ("ORA", "ZP",     op_read_alu(c_zp(), "ORA", "A")),
    0x15: ("ORA", "ZP,X",   op_read_alu(c_zp_x(), "ORA", "A")),
    0x0D: ("ORA", "Abs",    op_read_alu(c_abs(), "ORA", "A")),
    0x1D: ("ORA", "Abs,X",  op_read_alu(c_abs_x_read(), "ORA", "A")),
    0x19: ("ORA", "Abs,Y",  op_read_alu(c_abs_y_read(), "ORA", "A")),
    0x01: ("ORA", "(ZP,X)", op_read_alu(c_ind_x(), "ORA", "A")),
    0x11: ("ORA", "(ZP),Y", op_read_alu(c_ind_y_read(), "ORA", "A")),

    0x49: ("EOR", "#Imm",   FETCH + c_imm() + ["EOR(A, DL); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x45: ("EOR", "ZP",     op_read_alu(c_zp(), "EOR", "A")),
    0x55: ("EOR", "ZP,X",   op_read_alu(c_zp_x(), "EOR", "A")),
    0x4D: ("EOR", "Abs",    op_read_alu(c_abs(), "EOR", "A")),
    0x5D: ("EOR", "Abs,X",  op_read_alu(c_abs_x_read(), "EOR", "A")),
    0x59: ("EOR", "Abs,Y",  op_read_alu(c_abs_y_read(), "EOR", "A")),
    0x41: ("EOR", "(ZP,X)", op_read_alu(c_ind_x(), "EOR", "A")),
    0x51: ("EOR", "(ZP),Y", op_read_alu(c_ind_y_read(), "EOR", "A")),

    0x24: ("BIT", "ZP",     op_bit(c_zp())), 0x2C: ("BIT", "Abs",    op_bit(c_abs())),

    0xC9: ("CMP", "#Imm",   FETCH + c_imm() + ["CMP(A, DL); ALU_FLAGS_LD; END"]),
    0xC5: ("CMP", "ZP",     op_read_alu(c_zp(), "CMP", "A")),
    0xD5: ("CMP", "ZP,X",   op_read_alu(c_zp_x(), "CMP", "A")),
    0xCD: ("CMP", "Abs",    op_read_alu(c_abs(), "CMP", "A")),
    0xDD: ("CMP", "Abs,X",  op_read_alu(c_abs_x_read(), "CMP", "A")),
    0xD9: ("CMP", "Abs,Y",  op_read_alu(c_abs_y_read(), "CMP", "A")),
    0xC1: ("CMP", "(ZP,X)", op_read_alu(c_ind_x(), "CMP", "A")),
    0xD1: ("CMP", "(ZP),Y", op_read_alu(c_ind_y_read(), "CMP", "A")),

    0xE0: ("CPX", "#Imm",   FETCH + c_imm() + ["CMP(X, DL); ALU_FLAGS_LD; END"]),
    0xE4: ("CPX", "ZP",     op_read_alu(c_zp(), "CMP", "X")),
    0xEC: ("CPX", "Abs",    op_read_alu(c_abs(), "CMP", "X")),
    0xC0: ("CPY", "#Imm",   FETCH + c_imm() + ["CMP(Y, DL); ALU_FLAGS_LD; END"]),
    0xC4: ("CPY", "ZP",     op_read_alu(c_zp(), "CMP", "Y")),
    0xCC: ("CPY", "Abs",    op_read_alu(c_abs(), "CMP", "Y")),

    # --- 7. INC/DEC/RMW (Legal) ---
    0xE6: ("INC", "ZP",     op_rmw(c_zp(), "INC")),
    0xF6: ("INC", "ZP,X",   op_rmw(c_zp_x(), "INC")),
    0xEE: ("INC", "Abs",    op_rmw(c_abs(), "INC")),
    0xFE: ("INC", "Abs,X",  op_rmw(c_abs_x_read(), "INC")),
    0xC6: ("DEC", "ZP",     op_rmw(c_zp(), "DEC")),
    0xD6: ("DEC", "ZP,X",   op_rmw(c_zp_x(), "DEC")),
    0xCE: ("DEC", "Abs",    op_rmw(c_abs(), "DEC")),
    0xDE: ("DEC", "Abs,X",  op_rmw(c_abs_x_read(), "DEC")),

    0xE8: ("INX", "Impl", FETCH + ["INC(X); X := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0xC8: ("INY", "Impl", FETCH + ["INC(Y); Y := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0xCA: ("DEX", "Impl", FETCH + ["DEC(X); X := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x88: ("DEY", "Impl", FETCH + ["DEC(Y); Y := ALU_RESULT; ALU_FLAGS_LD; END"]),

    # --- 8. SHIFT (Legal) ---
    0x0A: ("ASL", "Acc",  FETCH + ["ASL(A); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x06: ("ASL", "ZP",   op_rmw(c_zp(), "ASL")),
    0x16: ("ASL", "ZP,X", op_rmw(c_zp_x(), "ASL")),
    0x0E: ("ASL", "Abs",  op_rmw(c_abs(), "ASL")),
    0x1E: ("ASL", "Abs,X",op_rmw(c_abs_x_read(), "ASL")),
    0x4A: ("LSR", "Acc",  FETCH + ["LSR(A); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x46: ("LSR", "ZP",   op_rmw(c_zp(), "LSR")),
    0x56: ("LSR", "ZP,X", op_rmw(c_zp_x(), "LSR")),
    0x4E: ("LSR", "Abs",  op_rmw(c_abs(), "LSR")),
    0x5E: ("LSR", "Abs,X",op_rmw(c_abs_x_read(), "LSR")),
    0x2A: ("ROL", "Acc",  FETCH + ["ROL(A); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x26: ("ROL", "ZP",   op_rmw(c_zp(), "ROL")),
    0x36: ("ROL", "ZP,X", op_rmw(c_zp_x(), "ROL")),
    0x2E: ("ROL", "Abs",  op_rmw(c_abs(), "ROL")),
    0x3E: ("ROL", "Abs,X",op_rmw(c_abs_x_read(), "ROL")),
    0x6A: ("ROR", "Acc",  FETCH + ["ROR(A); A := ALU_RESULT; ALU_FLAGS_LD; END"]),
    0x66: ("ROR", "ZP",   op_rmw(c_zp(), "ROR")),
    0x76: ("ROR", "ZP,X", op_rmw(c_zp_x(), "ROR")),
    0x6E: ("ROR", "Abs",  op_rmw(c_abs(), "ROR")),
    0x7E: ("ROR", "Abs,X",op_rmw(c_abs_x_read(), "ROR")),

    # --- 9. ILLEGAL OPCODES (Zoptymalizowane) ---
    0xA7: ("LAX", "ZP",     FETCH + c_zp() + ["DL := *{zeropage}; A := DL; X := DL; PASS(A); ALU_FLAGS_LD; END"]),
    0xB7: ("LAX", "ZP,Y",   FETCH + c_zp_y() + ["DL := *{zeropage}; DL := *{zeropage} + Y; A := DL; X := DL; PASS(A); ALU_FLAGS_LD; END"]),
    0xAF: ("LAX", "Abs",    FETCH + c_abs() + ["DL := *{latch}; A := DL; X := DL; PASS(A); ALU_FLAGS_LD; END"]),
    0xBF: ("LAX", "Abs,Y",  FETCH + c_abs_y_read() + ["DL := *{latch} + Y; A := DL; X := DL; PASS(A); ALU_FLAGS_LD; END"]),
    0xA3: ("LAX", "(ZP,X)", FETCH + c_ind_x() + ["DL := *{latch}; A := DL; X := DL; PASS(A); ALU_FLAGS_LD; END"]),
    0xB3: ("LAX", "(ZP),Y", FETCH + c_ind_y_read() + ["DL := *{latch} + Y; A := DL; X := DL; PASS(A); ALU_FLAGS_LD; END"]),

    0x87: ("SAX", "ZP",     op_sax(c_zp())),
    0x97: ("SAX", "ZP,Y",   op_sax(c_zp_y())),
    0x8F: ("SAX", "Abs",    op_sax(c_abs())),
    0x83: ("SAX", "(ZP,X)", op_sax(c_ind_x())),

    0xC7: ("DCP", "ZP",     op_complex_rmw(c_zp(), "DEC", "CMP")),
    0xD7: ("DCP", "ZP,X",   op_complex_rmw(c_zp_x(), "DEC", "CMP")),
    0xCF: ("DCP", "Abs",    op_complex_rmw(c_abs(), "DEC", "CMP")),
    0xDF: ("DCP", "Abs,X",  op_complex_rmw(c_abs_x_read(), "DEC", "CMP")),
    0xDB: ("DCP", "Abs,Y",  op_complex_rmw(c_abs_y_read(), "DEC", "CMP")),
    0xC3: ("DCP", "(ZP,X)", op_complex_rmw(c_ind_x(), "DEC", "CMP")),
    0xD3: ("DCP", "(ZP),Y", op_complex_rmw(c_ind_y_read(), "DEC", "CMP")),

    0xE7: ("ISC", "ZP",     op_complex_rmw(c_zp(), "INC", "SBC")),
    0xF7: ("ISC", "ZP,X",   op_complex_rmw(c_zp_x(), "INC", "SBC")),
    0xEF: ("ISC", "Abs",    op_complex_rmw(c_abs(), "INC", "SBC")),
    0xFF: ("ISC", "Abs,X",  op_complex_rmw(c_abs_x_read(), "INC", "SBC")),
    0xFB: ("ISC", "Abs,Y",  op_complex_rmw(c_abs_y_read(), "INC", "SBC")),
    0xE3: ("ISC", "(ZP,X)", op_complex_rmw(c_ind_x(), "INC", "SBC")),
    0xF3: ("ISC", "(ZP),Y", op_complex_rmw(c_ind_y_read(), "INC", "SBC")),

    0x07: ("SLO", "ZP",     op_complex_rmw(c_zp(), "ASL", "ORA")),
    0x17: ("SLO", "ZP,X",   op_complex_rmw(c_zp_x(), "ASL", "ORA")),
    0x0F: ("SLO", "Abs",    op_complex_rmw(c_abs(), "ASL", "ORA")),
    0x1F: ("SLO", "Abs,X",  op_complex_rmw(c_abs_x_read(), "ASL", "ORA")),
    0x1B: ("SLO", "Abs,Y",  op_complex_rmw(c_abs_y_read(), "ASL", "ORA")),
    0x03: ("SLO", "(ZP,X)", op_complex_rmw(c_ind_x(), "ASL", "ORA")),
    0x13: ("SLO", "(ZP),Y", op_complex_rmw(c_ind_y_read(), "ASL", "ORA")),

    0x27: ("RLA", "ZP",     op_complex_rmw(c_zp(), "ROL", "AND")),
    0x37: ("RLA", "ZP,X",   op_complex_rmw(c_zp_x(), "ROL", "AND")),
    0x2F: ("RLA", "Abs",    op_complex_rmw(c_abs(), "ROL", "AND")),
    0x3F: ("RLA", "Abs,X",  op_complex_rmw(c_abs_x_read(), "ROL", "AND")),
    0x3B: ("RLA", "Abs,Y",  op_complex_rmw(c_abs_y_read(), "ROL", "AND")),
    0x23: ("RLA", "(ZP,X)", op_complex_rmw(c_ind_x(), "ROL", "AND")),
    0x33: ("RLA", "(ZP),Y", op_complex_rmw(c_ind_y_read(), "ROL", "AND")),

    0x47: ("SRE", "ZP",     op_complex_rmw(c_zp(), "LSR", "EOR")),
    0x57: ("SRE", "ZP,X",   op_complex_rmw(c_zp_x(), "LSR", "EOR")),
    0x4F: ("SRE", "Abs",    op_complex_rmw(c_abs(), "LSR", "EOR")),
    0x5F: ("SRE", "Abs,X",  op_complex_rmw(c_abs_x_read(), "LSR", "EOR")),
    0x5B: ("SRE", "Abs,Y",  op_complex_rmw(c_abs_y_read(), "LSR", "EOR")),
    0x43: ("SRE", "(ZP,X)", op_complex_rmw(c_ind_x(), "LSR", "EOR")),
    0x53: ("SRE", "(ZP),Y", op_complex_rmw(c_ind_y_read(), "LSR", "EOR")),

    0x67: ("RRA", "ZP",     op_complex_rmw(c_zp(), "ROR", "ADC")),
    0x77: ("RRA", "ZP,X",   op_complex_rmw(c_zp_x(), "ROR", "ADC")),
    0x6F: ("RRA", "Abs",    op_complex_rmw(c_abs(), "ROR", "ADC")),
    0x7F: ("RRA", "Abs,X",  op_complex_rmw(c_abs_x_read(), "ROR", "ADC")),
    0x7B: ("RRA", "Abs,Y",  op_complex_rmw(c_abs_y_read(), "ROR", "ADC")),
    0x63: ("RRA", "(ZP,X)", op_complex_rmw(c_ind_x(), "ROR", "ADC")),
    0x73: ("RRA", "(ZP),Y", op_complex_rmw(c_ind_y_read(), "ROR", "ADC")),
}