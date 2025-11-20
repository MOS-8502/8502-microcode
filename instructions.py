# instructions.py

# ######################################
# ##      MAPA MIKROKODU DLA 8501     ##
# ######################################

MICROCODE_MAP = {
    # ==============================================================================
    # ==                            INSTRUKCJE SPECJALNE                          ==
    # ==============================================================================
    0x00: ("BRK", "Implied", [
        "IR := *PC",
        "*SP := PCH; SP -= 1",
        "*SP := PCL; SP -= 1",
        "*SP := P; SP -= 1",
        "DL := *fCPL",
        "ADL := DL",
        "DL := *fCPH",
        "ADH := DL; PC := {ADH, ADL}; SETF(I); END"
    ]),
    0x40: ("RTI", "Implied", [
        "IR := *PC; PC += 1",
        "SP += 1",
        "DL := *SP",
        "P := DL; SP += 1",
        "DL := *SP",
        "ADL := DL; SP += 1",
        "DL := *SP",
        "ADH := DL; PC := {ADH, ADL}; END"
    ]),
    0x60: ("RTS", "Implied", [
        "IR := *PC; PC += 1",
        "SP += 1",
        "DL := *SP",
        "ADL := DL; SP += 1",
        "DL := *SP",
        "ADH := DL",
        "PC := {ADH, ADL}",
        "PC += 1; END"
    ]),
    0xEA: ("NOP", "Implied", ["IR := *PC; PC += 1; END"]),

    # ==============================================================================
    # ==                        INSTRUKCJE ARYTMETYCZNE (ADC)                     ==
    # ==============================================================================
    0x69: ("ADC", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x65: ("ADC", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "ADC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x75: ("ADC", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "ADC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x6D: ("ADC", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "ADC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x7D: ("ADC", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "ADC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x79: ("ADC", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + Y",
        "ADC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x61: ("ADC", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}",
        "ADC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x71: ("ADC", "(zp),Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}+Y",
        "ADC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),

    # ==============================================================================
    # ==                        INSTRUKCJE ARYTMETYCZNE (SBC)                     ==
    # ==============================================================================
    0xE9: ("SBC", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "SBC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0xE5: ("SBC", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "SBC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0xF5: ("SBC", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "SBC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0xED: ("SBC", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "SBC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0xFD: ("SBC", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "SBC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0xF9: ("SBC", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + Y",
        "SBC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0xE1: ("SBC", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}",
        "SBC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0xF1: ("SBC", "(zp),Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}+Y",
        "SBC(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),

    # ==============================================================================
    # ==                          INSTRUKCJE LOGICZNE (AND)                       ==
    # ==============================================================================
    0x29: ("AND", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "AND(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x25: ("AND", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "AND(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x35: ("AND", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "AND(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x2D: ("AND", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "AND(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x3D: ("AND", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "AND(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x39: ("AND", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + Y",
        "AND(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x21: ("AND", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}",
        "AND(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x31: ("AND", "(zp),Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}+Y",
        "AND(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),

    # ==============================================================================
    # ==                           INSTRUKCJE LOGICZNE (ORA)                      ==
    # ==============================================================================
    0x09: ("ORA", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ORA(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x05: ("ORA", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "ORA(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x15: ("ORA", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "ORA(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x0D: ("ORA", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "ORA(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x1D: ("ORA", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "ORA(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x19: ("ORA", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + Y",
        "ORA(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x01: ("ORA", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}",
        "ORA(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x11: ("ORA", "(zp),Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}+Y",
        "ORA(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),

    # ==============================================================================
    # ==                           INSTRUKCJE LOGICZNE (EOR)                      ==
    # ==============================================================================
    0x49: ("EOR", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "EOR(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x45: ("EOR", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "EOR(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x55: ("EOR", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "EOR(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x4D: ("EOR", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "EOR(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x5D: ("EOR", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "EOR(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x59: ("EOR", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + Y",
        "EOR(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x41: ("EOR", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}",
        "EOR(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x51: ("EOR", "(zp),Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}+Y",
        "EOR(A, DL); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),

    # ==============================================================================
    # ==                             PORÓWNANIA I TESTY                           ==
    # ==============================================================================
    0xC9: ("CMP", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "CMP(A, DL); ALU_FLAGS_LD; END"
    ]),
    0xC5: ("CMP", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "CMP(A, DL); ALU_FLAGS_LD; END"
    ]),
    0xD5: ("CMP", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "CMP(A, DL); ALU_FLAGS_LD; END"
    ]),
    0xCD: ("CMP", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "CMP(A, DL); ALU_FLAGS_LD; END"
    ]),
    0xDD: ("CMP", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "CMP(A, DL); ALU_FLAGS_LD; END"
    ]),
    0xD9: ("CMP", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + Y",
        "CMP(A, DL); ALU_FLAGS_LD; END"
    ]),
    0xC1: ("CMP", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}",
        "CMP(A, DL); ALU_FLAGS_LD; END"
    ]),
    0xD1: ("CMP", "(zp),Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}+Y",
        "CMP(A, DL); ALU_FLAGS_LD; END"
    ]),
    0xE0: ("CPX", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "CMP(X, DL); ALU_FLAGS_LD; END"
    ]),
    0xE4: ("CPX", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "CMP(X, DL); ALU_FLAGS_LD; END"
    ]),
    0xEC: ("CPX", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "CMP(X, DL); ALU_FLAGS_LD; END"
    ]),
    0xC0: ("CPY", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "CMP(Y, DL); ALU_FLAGS_LD; END"
    ]),
    0xC4: ("CPY", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "CMP(Y, DL); ALU_FLAGS_LD; END"
    ]),
    0xCC: ("CPY", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "CMP(Y, DL); ALU_FLAGS_LD; END"
    ]),
    0x24: ("BIT", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "BIT(A, DL); ALU_FLAGS_LD; END"
    ]),
    0x2C: ("BIT", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "BIT(A, DL); ALU_FLAGS_LD; END"
    ]),

    # ==============================================================================
    # ==                             INKREMENTACJA / DEKREMENTACJA                ==
    # ==============================================================================
    0xE8: ("INX", "Implied", [
        "IR := *PC; PC += 1",
        "INC(X); ALU_FLAGS_LD",
        "X := ALU_RESULT; END"
    ]),
    0xC8: ("INY", "Implied", [
        "IR := *PC; PC += 1",
        "INC(Y); ALU_FLAGS_LD",
        "Y := ALU_RESULT; END"
    ]),
    0xCA: ("DEX", "Implied", [
        "IR := *PC; PC += 1",
        "DEC(X); ALU_FLAGS_LD",
        "X := ALU_RESULT; END"
    ]),
    0x88: ("DEY", "Implied", [
        "IR := *PC; PC += 1",
        "DEC(Y); ALU_FLAGS_LD",
        "Y := ALU_RESULT; END"
    ]),
    0x1A: ("INC", "Accumulator", [
        "IR := *PC; PC += 1",
        "INC(A); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x3A: ("DEC", "Accumulator", [
        "IR := *PC; PC += 1",
        "DEC(A); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0xE6: ("INC", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "TMP := DL",
        "INC(TMP); ALU_FLAGS_LD",
        "* {zeropage} := ALU_RESULT; END"
    ]),
    0xF6: ("INC", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "TMP := DL",
        "INC(TMP); ALU_FLAGS_LD",
        "* {zeropage} + X := ALU_RESULT; END"
    ]),
    0xEE: ("INC", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "TMP := DL",
        "INC(TMP); ALU_FLAGS_LD",
        "* {latch} := ALU_RESULT; END"
    ]),
    0xFE: ("INC", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "TMP := DL",
        "INC(TMP); ALU_FLAGS_LD",
        "* {latch} + X := ALU_RESULT; END"
    ]),
    0xC6: ("DEC", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "TMP := DL",
        "DEC(TMP); ALU_FLAGS_LD",
        "* {zeropage} := ALU_RESULT; END"
    ]),
    0xD6: ("DEC", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "TMP := DL",
        "DEC(TMP); ALU_FLAGS_LD",
        "* {zeropage} + X := ALU_RESULT; END"
    ]),
    0xCE: ("DEC", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "TMP := DL",
        "DEC(TMP); ALU_FLAGS_LD",
        "* {latch} := ALU_RESULT; END"
    ]),
    0xDE: ("DEC", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "TMP := DL",
        "DEC(TMP); ALU_FLAGS_LD",
        "* {latch} + X := ALU_RESULT; END"
    ]),

    # ==============================================================================
    # ==                             PRZESUNIĘCIA I ROTACJE                       ==
    # ==============================================================================
    0x0A: ("ASL", "Accumulator", [
        "IR := *PC; PC += 1",
        "ASL(A); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x06: ("ASL", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "TMP := DL",
        "ASL(TMP); ALU_FLAGS_LD",
        "* {zeropage} := ALU_RESULT; END"
    ]),
    0x16: ("ASL", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "TMP := DL",
        "ASL(TMP); ALU_FLAGS_LD",
        "* {zeropage} + X := ALU_RESULT; END"
    ]),
    0x0E: ("ASL", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "TMP := DL",
        "ASL(TMP); ALU_FLAGS_LD",
        "* {latch} := ALU_RESULT; END"
    ]),
    0x1E: ("ASL", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "TMP := DL",
        "ASL(TMP); ALU_FLAGS_LD",
        "* {latch} + X := ALU_RESULT; END"
    ]),
    0x4A: ("LSR", "Accumulator", [
        "IR := *PC; PC += 1",
        "LSR(A); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x46: ("LSR", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "TMP := DL",
        "LSR(TMP); ALU_FLAGS_LD",
        "* {zeropage} := ALU_RESULT; END"
    ]),
    0x56: ("LSR", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "TMP := DL",
        "LSR(TMP); ALU_FLAGS_LD",
        "* {zeropage} + X := ALU_RESULT; END"
    ]),
    0x4E: ("LSR", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "TMP := DL",
        "LSR(TMP); ALU_FLAGS_LD",
        "* {latch} := ALU_RESULT; END"
    ]),
    0x5E: ("LSR", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "TMP := DL",
        "LSR(TMP); ALU_FLAGS_LD",
        "* {latch} + X := ALU_RESULT; END"
    ]),
    0x2A: ("ROL", "Accumulator", [
        "IR := *PC; PC += 1",
        "ROL(A); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x26: ("ROL", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "TMP := DL",
        "ROL(TMP); ALU_FLAGS_LD",
        "* {zeropage} := ALU_RESULT; END"
    ]),
    0x36: ("ROL", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "TMP := DL",
        "ROL(TMP); ALU_FLAGS_LD",
        "* {zeropage} + X := ALU_RESULT; END"
    ]),
    0x2E: ("ROL", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "TMP := DL",
        "ROL(TMP); ALU_FLAGS_LD",
        "* {latch} := ALU_RESULT; END"
    ]),
    0x3E: ("ROL", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "TMP := DL",
        "ROL(TMP); ALU_FLAGS_LD",
        "* {latch} + X := ALU_RESULT; END"
    ]),
    0x6A: ("ROR", "Accumulator", [
        "IR := *PC; PC += 1",
        "ROR(A); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x66: ("ROR", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "TMP := DL",
        "ROR(TMP); ALU_FLAGS_LD",
        "* {zeropage} := ALU_RESULT; END"
    ]),
    0x76: ("ROR", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "TMP := DL",
        "ROR(TMP); ALU_FLAGS_LD",
        "* {zeropage} + X := ALU_RESULT; END"
    ]),
    0x6E: ("ROR", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "TMP := DL",
        "ROR(TMP); ALU_FLAGS_LD",
        "* {latch} := ALU_RESULT; END"
    ]),
    0x7E: ("ROR", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "TMP := DL",
        "ROR(TMP); ALU_FLAGS_LD",
        "* {latch} + X := ALU_RESULT; END"
    ]),

    # ==============================================================================
    # ==                             ŁADOWANIE / ZAPIS DO PAMIĘCI                 ==
    # ==============================================================================
    0xA9: ("LDA", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "A := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xA5: ("LDA", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "A := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xB5: ("LDA", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "A := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xAD: ("LDA", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "A := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xBD: ("LDA", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "A := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xB9: ("LDA", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + Y",
        "A := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xA1: ("LDA", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}",
        "A := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xB1: ("LDA", "(zp),Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}+Y",
        "A := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xA2: ("LDX", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "X := DL",
        "PASS(X); ALU_FLAGS_LD; END"
    ]),
    0xA6: ("LDX", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "X := DL",
        "PASS(X); ALU_FLAGS_LD; END"
    ]),
    0xB6: ("LDX", "Zero Page,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + Y",
        "X := DL",
        "PASS(X); ALU_FLAGS_LD; END"
    ]),
    0xAE: ("LDX", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "X := DL",
        "PASS(X); ALU_FLAGS_LD; END"
    ]),
    0xBE: ("LDX", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + Y",
        "X := DL",
        "PASS(X); ALU_FLAGS_LD; END"
    ]),
    0xA0: ("LDY", "#Immediate", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "Y := DL",
        "PASS(Y); ALU_FLAGS_LD; END"
    ]),
    0xA4: ("LDY", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "Y := DL",
        "PASS(Y); ALU_FLAGS_LD; END"
    ]),
    0xB4: ("LDY", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + X",
        "Y := DL",
        "PASS(Y); ALU_FLAGS_LD; END"
    ]),
    0xAC: ("LDY", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "Y := DL",
        "PASS(Y); ALU_FLAGS_LD; END"
    ]),
    0xBC: ("LDY", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + X",
        "Y := DL",
        "PASS(Y); ALU_FLAGS_LD; END"
    ]),
    0x85: ("STA", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage} := A; END"
    ]),
    0x95: ("STA", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "* {zeropage} + X := A; END"
    ]),
    0x8D: ("STA", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "* {latch} := A; END"
    ]),
    0x9D: ("STA", "Absolute,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "* {latch}+X",
        "* {latch} + X := A; END"
    ]),
    0x99: ("STA", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "* {latch}+Y",
        "* {latch} + Y := A; END"
    ]),
    0x81: ("STA", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "* {latch} := A; END"
    ]),
    0x91: ("STA", "(zp),Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "* {latch}+Y := A; END"
    ]),
    0x86: ("STX", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage} := X; END"
    ]),
    0x96: ("STX", "Zero Page,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "* {zeropage} + Y := X; END"
    ]),
    0x8E: ("STX", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "* {latch} := X; END"
    ]),
    0x84: ("STY", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage} := Y; END"
    ]),
    0x94: ("STY", "Zero Page,X", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "* {zeropage} + X := Y; END"
    ]),
    0x8C: ("STY", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "* {latch} := Y; END"
    ]),

    # ==============================================================================
    # ==                             TRANSFERY I OPERACJE NA STOSIE               ==
    # ==============================================================================
    0xAA: ("TAX", "Implied", [
        "IR := *PC; PC += 1",
        "PASS(A); ALU_FLAGS_LD",
        "X := ALU_RESULT; END"
    ]),
    0xA8: ("TAY", "Implied", [
        "IR := *PC; PC += 1",
        "PASS(A); ALU_FLAGS_LD",
        "Y := ALU_RESULT; END"
    ]),
    0x8A: ("TXA", "Implied", [
        "IR := *PC; PC += 1",
        "PASS(X); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0x98: ("TYA", "Implied", [
        "IR := *PC; PC += 1",
        "PASS(Y); ALU_FLAGS_LD",
        "A := ALU_RESULT; END"
    ]),
    0xBA: ("TSX", "Implied", [
        "IR := *PC; PC += 1",
        "PASS(SP); ALU_FLAGS_LD",
        "X := ALU_RESULT; END"
    ]),
    0x9A: ("TXS", "Implied", [
        "IR := *PC; PC += 1",
        "SP := X; END"
    ]),
    0x48: ("PHA", "Implied", [
        "IR := *PC; PC += 1",
        "*SP := A; SP -= 1; END"
    ]),
    0x68: ("PLA", "Implied", [
        "IR := *PC; PC += 1",
        "SP += 1",
        "DL := *SP",
        "A := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0x08: ("PHP", "Implied", [
        "IR := *PC; PC += 1",
        "*SP := P; SP -= 1; END"
    ]),
    0x28: ("PLP", "Implied", [
        "IR := *PC; PC += 1",
        "SP += 1",
        "DL := *SP",
        "P := DL; END"
    ]),

    # ==============================================================================
    # ==                             SKOKI I PODPROGRAMY                          ==
    # ==============================================================================
    0x4C: ("JMP", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "PC := {ADH, ADL}; END"
    ]),
    0x6C: ("JMP", "Indirect", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "ADL := DL",
        "DL := *{latch_inc}",
        "ADH := DL; PC := {ADH, ADL}; END"
    ]),
    0x20: ("JSR", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "",
        "*SP := PCH; SP -= 1",
        "DL := *PC",
        "ADH := DL",
        "*SP := PCL; SP -= 1",
        "PC := {ADH, ADL}; END"
    ]),
    0x10: ("BPL", "Relative", [
        "IR := *PC; PC += 1",
        "ADL := *PC; PC += 1; TEST_BRANCH_EN; END",
        "PC := PC + ADL; END"
    ]),
    0x30: ("BMI", "Relative", [
        "IR := *PC; PC += 1",
        "ADL := *PC; PC += 1; TEST_BRANCH_EN; END",
        "PC := PC + ADL; END"
    ]),
    0x50: ("BVC", "Relative", [
        "IR := *PC; PC += 1",
        "ADL := *PC; PC += 1; TEST_BRANCH_EN; END",
        "PC := PC + ADL; END"
    ]),
    0x70: ("BVS", "Relative", [
        "IR := *PC; PC += 1",
        "ADL := *PC; PC += 1; TEST_BRANCH_EN; END",
        "PC := PC + ADL; END"
    ]),
    0x90: ("BCC", "Relative", [
        "IR := *PC; PC += 1",
        "ADL := *PC; PC += 1; TEST_BRANCH_EN; END",
        "PC := PC + ADL; END"
    ]),
    0xB0: ("BCS", "Relative", [
        "IR := *PC; PC += 1",
        "ADL := *PC; PC += 1; TEST_BRANCH_EN; END",
        "PC := PC + ADL; END"
    ]),
    0xD0: ("BNE", "Relative", [
        "IR := *PC; PC += 1",
        "ADL := *PC; PC += 1; TEST_BRANCH_EN; END",
        "PC := PC + ADL; END"
    ]),
    0xF0: ("BEQ", "Relative", [
        "IR := *PC; PC += 1",
        "ADL := *PC; PC += 1; TEST_BRANCH_EN; END",
        "PC := PC + ADL; END"
    ]),

    # ==============================================================================
    # ==                             OPERACJE NA FLAGACH                          ==
    # ==============================================================================
    0x18: ("CLC", "Implied", ["IR := *PC; PC += 1", "CLRF(C); END"]),
    0x38: ("SEC", "Implied", ["IR := *PC; PC += 1", "SETF(C); END"]),
    0x58: ("CLI", "Implied", ["IR := *PC; PC += 1", "CLRF(I); END"]),
    0x78: ("SEI", "Implied", ["IR := *PC; PC += 1", "SETF(I); END"]),
    0xB8: ("CLV", "Implied", ["IR := *PC; PC += 1", "CLRF(V); END"]),
    0xD8: ("CLD", "Implied", ["IR := *PC; PC += 1", "CLRF(D); END"]),
    0xF8: ("SED", "Implied", ["IR := *PC; PC += 1", "SETF(D); END"]),

    # ==============================================================================
    # ==                             INSTRUKCJE NIEDOKUMENTOWANE                  ==
    # ==============================================================================
    0x83: ("SAX", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "AND(A, X)",
        "* {latch} := ALU_RESULT; END"
    ]),
    0x87: ("SAX", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "AND(A, X)",
        "* {zeropage} := ALU_RESULT; END"
    ]),
    0x8F: ("SAX", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "AND(A, X)",
        "* {latch} := ALU_RESULT; END"
    ]),
    0x97: ("SAX", "Zero Page,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "AND(A, X)",
        "* {zeropage} + Y := ALU_RESULT; END"
    ]),
    0xA3: ("LAX", "(zp,X)", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "ADL := {calculate_zp_x_pointer}",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}",
        "A := DL; X := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xA7: ("LAX", "Zero Page", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage}",
        "A := DL; X := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xAF: ("LAX", "Absolute", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch}",
        "A := DL; X := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xB3: ("LAX", "(zp),Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *{zeropage_indirect}",
        "TMP := DL",
        "DL := *{zeropage_indirect_inc}",
        "ADH := DL; ADL := TMP",
        "DL := *{latch}+Y",
        "A := DL; X := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xB7: ("LAX", "Zero Page,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "* {zeropage}",
        "DL := *{zeropage} + Y",
        "A := DL; X := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
    0xBF: ("LAX", "Absolute,Y", [
        "IR := *PC; PC += 1",
        "DL := *PC; PC += 1",
        "ADL := DL",
        "DL := *PC; PC += 1",
        "ADH := DL",
        "DL := *{latch} + Y",
        "A := DL; X := DL",
        "PASS(A); ALU_FLAGS_LD; END"
    ]),
}