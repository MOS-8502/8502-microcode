# compiler.py

# -*- coding: utf-8 -*-

# ==============================================================================
#  SEKCJA 0: IMPORT
# ==============================================================================
import csv

try:
    from instructions import MICROCODE_MAP
except ImportError:
    print("BŁĄD: Nie znaleziono pliku 'instructions.py'.")
    print("Upewnij się, że plik z definicjami instrukcji znajduje się w tym samym folderze.")
    exit()

# ##############################################################################
# ## UNIWERSALNY GENERATOR MIKROKODU DLA PROCESORA 8501 (PROJEKT UŻYTKOWNIKA) ##
# ##############################################################################

# ==============================================================================
#  SEKCJA 1: DEFINICJE KODÓW STERUJĄCYCH
# ==============================================================================
ALU_OP_CODES = {
    "none": 0b0000, "adc": 0b0001, "sbc": 0b0010, "and": 0b0011,
    "ora": 0b0100, "xor": 0b0101, "bit": 0b0110, "cmp": 0b0111,
    "asl": 0b1000, "lsr": 0b1001, "rol": 0b1010, "ror": 0b1011,
    "inc": 0b1100, "dec": 0b1101, "pass": 0b1110, "out": 0b1111
}

REG_OUT_CODES = {
    "a": 0b101, "x": 0b100, "y": 0b011,
    "sp": 0b010, "p": 0b001, "none": 0b000,
    "tmp": 0b110, "dl": 0b111
}

ADDR_SOURCE_CODES = {
    "pc": 0b0001,
    "stack": 0b0010,
    "latch": 0b0011,
    "irq_lsb": 0b0110,
    "irq_msb": 0b0111,
    "zeropage": 0b1000,
    "pc_plus_offset": 0b1000,
    "zeropage_indirect": 0b1001,
    "zeropage_indirect_inc": 0b1010,
    "calculate_zp_x_pointer": 0b1011,
    "latch_inc": 0b1100
}


# ==============================================================================
#  SEKCJA 2: GŁÓWNA LOGIKA - PARSER I ASSEMBLER
# ==============================================================================
def generate_microcode(symbolic_code: str) -> tuple[int, int, int]:
    """
    Tłumaczy symboliczną mikroinstrukcję na trzy 16-bitowe słowa sterujące.
    """
    signals = {
        "alu_flags_ld": False, "alu_op_key": "none", "reg_a_load_en": False,
        "reg_x_load_en": False, "reg_y_load_en": False, "reg_sp_load_en": False,
        "reg_p_load_en": False, "reg_out_key": "none", "pc_inc_en": False,
        "pc_load_en": False, "pc_out_addr_en": False, "addr_source_key": "none",
        "adh_load_en": False, "adl_load_en": False, "x_add_to_addr_en": False,
        "y_add_to_addr_en": False, "pch_out_en": False, "pcl_out_en": False,
        "sp_int_inc_en": False, "sp_int_dec_en": False, "mem_read_en": False,
        "mem_write_en": False, "data_bus_in_en": False, "data_bus_out_en": False,
        "addr_out_bus_en": False, "p_c_set_en": False, "p_c_clr_en": False,
        "p_d_set_en": False, "p_d_clr_en": False, "p_i_set_en": False,
        "p_i_clr_en": False, "p_v_clr_en": False, "test_branch_en": False,
        "cpu_master_reset_en": False, "reset_cycle_counter_en": False,
        "load_ir_en": False, "tmp_load_en": False
    }

    if not symbolic_code:
        return 0, 0, 0

    operations = [op.strip() for op in symbolic_code.lower().split(';')]

    for op in operations:
        # --- Proste operacje ---
        if op == "sp += 1":
            signals["sp_int_inc_en"] = True
        elif op == "sp -= 1":
            signals["sp_int_dec_en"] = True
        elif op == "pc += 1":
            signals["pc_inc_en"] = True
        elif op == "end":
            signals["reset_cycle_counter_en"] = True
        elif op == "alu_flags_ld":
            signals["alu_flags_ld"] = True
        elif op.startswith('clrf('):
            signals[f"p_{op[5:-1]}_clr_en"] = True
        elif op.startswith('setf('):
            signals[f"p_{op[5:-1]}_set_en"] = True
        elif op == "test_branch_en":
            signals["test_branch_en"] = True

        # --- Operacje złożone ---
        else:
            is_assignment = ":=" in op
            dest, source = (op.split(':=', 1) if is_assignment else ("", op))
            dest, source = dest.strip(), source.strip()

            # --- Analiza Źródła ---
            if "+ x" in source:
                signals["x_add_to_addr_en"] = True
                source = source.replace("+ x", "").strip()
            if "+ y" in source:
                signals["y_add_to_addr_en"] = True
                source = source.replace("+ y", "").strip()

            if '(' in source and source.endswith(')'):
                op_key, operands = source.split('(', 1)
                operands = operands[:-1].strip()
                signals["alu_op_key"] = op_key
                if ',' in operands:
                    reg_operand, mem_operand = [p.strip() for p in operands.split(',', 1)]
                    signals["reg_out_key"] = reg_operand
                    source = mem_operand
                else:
                    signals["reg_out_key"] = operands
                    source = ""

            if source == "alu_result":
                signals["alu_op_key"] = "out"
            elif source in REG_OUT_CODES:
                signals["reg_out_key"] = source
            elif source in ["pch", "pcl"]:
                signals[f"{source}_out_en"] = True

            elif source.startswith('*'):
                signals["mem_read_en"] = True
                signals["data_bus_in_en"] = True  # To teraz zatrzaskuje DL
                signals["addr_out_bus_en"] = True
                source_addr = source[1:]
                if source_addr == "{0x00, adl}":
                    signals["addr_source_key"] = "zeropage"
                elif source_addr == "{latch}" or source_addr == "{adh, adl}":
                    signals["addr_source_key"] = "latch"
                elif source_addr == "pc":
                    signals["addr_source_key"] = "pc"
                # ... inne tryby odczytu

            # --- Analiza Celu ---
            if dest:
                if dest in ["a", "x", "y", "sp", "p", "tmp", "ir", "adh", "adl"]:
                    signals[f"{'reg_' if dest not in ['tmp', 'ir', 'adh', 'adl', 'p'] else ''}{dest}_load_en"] = True
                elif dest.startswith('*'):
                    signals["mem_write_en"] = True
                    signals["data_bus_out_en"] = True
                    signals["addr_out_bus_en"] = True
                    dest_addr = dest[1:].strip()
                    if "+ x" in dest_addr:
                        signals["x_add_to_addr_en"] = True
                        dest_addr = dest_addr.replace("+ x", "").strip()
                    if "+ y" in dest_addr:
                        signals["y_add_to_addr_en"] = True
                        dest_addr = dest_addr.replace("+ y", "").strip()
                    if dest_addr == "{0x00, adl}": signals["addr_source_key"] = "zeropage"
                    elif dest_addr == "{latch}" or dest_addr == "{adh, adl}": signals["addr_source_key"] = "latch"
                    elif dest_addr == "sp": signals["addr_source_key"] = "stack"

    # --- ASSEMBLER - Składanie słów mikrokodu ---
    w2 = ((1 if signals["alu_flags_ld"] else 0) << 15 |
          ALU_OP_CODES.get(signals["alu_op_key"], 0) << 11 |
          (1 if signals["reg_a_load_en"] else 0) << 10 |
          (1 if signals["reg_x_load_en"] else 0) << 9 |
          (1 if signals["reg_y_load_en"] else 0) << 8 |
          (1 if signals["reg_sp_load_en"] else 0) << 7 |
          (1 if signals["reg_p_load_en"] else 0) << 6 |
          REG_OUT_CODES.get(signals["reg_out_key"], 0) << 3 |
          (1 if signals["pc_inc_en"] else 0) << 2 |
          (1 if signals["pc_load_en"] else 0) << 1 |
          (1 if signals["pc_out_addr_en"] else 0))

    w1 = (ADDR_SOURCE_CODES.get(signals["addr_source_key"], 0) << 12 |
          (1 if signals["adh_load_en"] else 0) << 11 |
          (1 if signals["adl_load_en"] else 0) << 10 |
          (1 if signals["x_add_to_addr_en"] else 0) << 9 |
          (1 if signals["y_add_to_addr_en"] else 0) << 8 |
          (1 if signals["pch_out_en"] else 0) << 7 |
          (1 if signals["pcl_out_en"] else 0) << 6 |
          (1 if signals["sp_int_inc_en"] else 0) << 5 |
          (1 if signals["sp_int_dec_en"] else 0) << 4 |
          (1 if signals["mem_read_en"] else 0) << 3 |
          (1 if signals["mem_write_en"] else 0) << 2 |
          (1 if signals["data_bus_in_en"] else 0) << 1 |
          (1 if signals["data_bus_out_en"] else 0))

    w0 = ((1 if signals["p_c_set_en"] else 0) << 14 |
          (1 if signals["p_c_clr_en"] else 0) << 13 |
          (1 if signals["p_d_set_en"] else 0) << 12 |
          (1 if signals["p_d_clr_en"] else 0) << 11 |
          (1 if signals["p_i_set_en"] else 0) << 10 |
          (1 if signals["p_i_clr_en"] else 0) << 9 |
          (1 if signals["p_v_clr_en"] else 0) << 8 |
          (1 if signals["tmp_load_en"] else 0) << 7 |
          (1 if signals["addr_out_bus_en"] else 0) << 4 |
          (1 if signals["test_branch_en"] else 0) << 3 |
          (1 if signals["cpu_master_reset_en"] else 0) << 2 |
          (1 if signals["reset_cycle_counter_en"] else 0) << 1 |
          (1 if signals["load_ir_en"] else 0))

    return w2, w1, w0


# ==============================================================================
#  SEKCJA 3: FUNKCJE POMOCNICZE
# ==============================================================================
def translate_instruction(name: str, cycles: list):
    """Tłumaczy całą instrukcję i drukuje wyniki w czytelnej formie."""
    print(f"--- Mikrokod dla instrukcji: {name} ---")
    for i, cycle_code in enumerate(cycles):
        w2, w1, w0 = generate_microcode(cycle_code)
        print(f"Cykl {i}: {cycle_code:<48} -> W2=0x{w2:04X}, W1=0x{w1:04X}, W0=0x{w0:04X}")
    print("-" * (73 + len(name)))


def generate_rom_files(microcode_map, num_opcodes=256, max_cycles=8):
    """
    Generuje 24 pliki tekstowe dla architektury ROM z 8 bankami.
    """
    print("\n--- Generowanie plików tekstowych ROM ---")

    num_banks = max_cycles
    words_per_bank = num_opcodes

    roms_w2 = [["0000"] * words_per_bank for _ in range(num_banks)]
    roms_w1 = [["0000"] * words_per_bank for _ in range(num_banks)]
    roms_w0 = [["0000"] * words_per_bank for _ in range(num_banks)]

    for opcode, data in microcode_map.items():
        _mnemonic, _addressing_mode, cycles = data
        for cycle_index, symbolic_code in enumerate(cycles):
            if cycle_index >= max_cycles:
                continue

            w2, w1, w0 = generate_microcode(symbolic_code)

            bank_index = cycle_index
            address_in_bank = opcode

            roms_w2[bank_index][address_in_bank] = f"{w2:04X}"
            roms_w1[bank_index][address_in_bank] = f"{w1:04X}"
            roms_w0[bank_index][address_in_bank] = f"{w0:04X}"

    try:
        for i in range(num_banks):
            with open(f"w2_bank{i}.txt", "w") as f:
                f.write("\n".join(roms_w2[i]))
            with open(f"w1_bank{i}.txt", "w") as f:
                f.write("\n".join(roms_w1[i]))
            with open(f"w0_bank{i}.txt", "w") as f:
                f.write("\n".join(roms_w0[i]))
        print(f"Pomyślnie wygenerowano {num_banks * 3} plików tekstowych.")
    except IOError as e:
        print(f"Błąd podczas zapisu plików tekstowych: {e}")


def generate_csv_log(microcode_map):
    """Generuje plik CSV z kompletnym logiem mikrokodu."""
    print("\n--- Generowanie pliku logu CSV ---")
    try:
        with open("microcode_log.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(['Opcode', 'Mnemonic', 'Addressing', 'Cycle', 'Symbolic Code', 'W2', 'W1', 'W0'])

            for opcode, data in sorted(microcode_map.items()):
                mnemonic, addressing_mode, cycles = data
                for cycle_index, symbolic_code in enumerate(cycles):
                    w2, w1, w0 = generate_microcode(symbolic_code)
                    writer.writerow([
                        f"{opcode:02X}",
                        mnemonic,
                        addressing_mode,
                        cycle_index,
                        symbolic_code if symbolic_code else "NO-OP",
                        f"{w2:04X}",
                        f"{w1:04X}",
                        f"{w0:04X}"
                    ])
        print("Pomyślnie wygenerowano plik microcode_log.csv")
    except IOError as e:
        print(f"Błąd podczas zapisu pliku CSV: {e}")


# ==============================================================================
#  SEKCJA 4: GŁÓWNY BLOK WYKONAWCZY
# ==============================================================================
if __name__ == "__main__":
    print("--- Walidacja mapy mikrokodu ---")
    error_found = False
    for opcode, data in MICROCODE_MAP.items():
        mnemonic, addressing_mode, cycles = data
        if len(cycles) > 8:
            print(
                f"BŁĄD KRYTYCZNY: Instrukcja ${opcode:02X} ({mnemonic} {addressing_mode}) ma {len(cycles)} cykli (limit to 8)!")
            error_found = True

    if error_found:
        print("Przerwano kompilację z powodu błędów.")
        exit(1)
    else:
        print("Walidacja zakończona pomyślnie.")

    print("\n--- Tłumaczenie mikrokodów dla weryfikacji ---")
    if not MICROCODE_MAP:
        print("Mapa mikrokodu (MICROCODE_MAP) jest pusta.")
    else:
        for opcode, data in sorted(MICROCODE_MAP.items()):
            mnemonic, addressing_mode, cycles = data
            translate_instruction(f"{opcode:02X} ({mnemonic} {addressing_mode})", cycles)
            print()

    generate_rom_files(MICROCODE_MAP)
    generate_csv_log(MICROCODE_MAP)