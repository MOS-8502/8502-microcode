# ucode.py
# -*- coding: utf-8 -*-

import csv
import os

try:
    from instructions import MICROCODE_MAP
except ImportError:
    print("BŁĄD: Nie znaleziono pliku 'instructions.py'.")
    print("Upewnij się, że plik z definicjami instrukcji znajduje się w tym samym folderze.")
    exit()

# Konfiguracja folderu wyjściowego
OUTPUT_DIR = "build"

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
#  SEKCJA 2: PARSER I ASSEMBLER
# ==============================================================================
def generate_microcode(symbolic_code: str) -> tuple[int, int, int]:
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
        "load_ir_en": False, "tmp_load_en": False, "p_b_force_one_en": False
    }

    if not symbolic_code:
        return 0, 0, 0

    operations = [op.strip() for op in symbolic_code.lower().split(';')]

    for op in operations:
        if not op: continue

        # --- Proste flagi i operacje ---
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
        elif op == "test_branch_en":
            signals["test_branch_en"] = True
        elif op.startswith('clrf('):
            signals[f"p_{op[5:-1]}_clr_en"] = True
        elif op.startswith('setf('):
            signals[f"p_{op[5:-1]}_set_en"] = True
        elif op.startswith('setf('):
            flag_name = op[5:-1].lower()
            if flag_name == 'b':
                signals["p_b_force_one_en"] = True
            else:
                signals[f"p_{flag_name}_set_en"] = True
        # --- Przypisania (:=) ---
        else:
            is_assignment = ":=" in op
            dest, source = (op.split(':=', 1) if is_assignment else ("", op))
            dest, source = dest.strip(), source.strip()

            # 1. Modyfikatory źródła (+ X, + Y)
            if "+ x" in source:
                signals["x_add_to_addr_en"] = True
                source = source.replace("+ x", "").strip()
            if "+ y" in source:
                signals["y_add_to_addr_en"] = True
                source = source.replace("+ y", "").strip()

            # 2. ALU Operations
            if '(' in source and source.endswith(')'):
                op_key, operands = source.split('(', 1)
                operands = operands[:-1].strip()
                signals["alu_op_key"] = op_key
                if ',' in operands:
                    reg_operand, mem_operand = [p.strip() for p in operands.split(',', 1)]
                    signals["reg_out_key"] = reg_operand
                    source = mem_operand
                else:
                    if operands in REG_OUT_CODES:
                        signals["reg_out_key"] = operands
                    source = ""

            # 3. Analiza Źródła
            if source == "alu_result":
                signals["alu_op_key"] = "out"
            elif source in REG_OUT_CODES:
                signals["reg_out_key"] = source
            elif source in ["pch", "pcl"]:
                signals[f"{source}_out_en"] = True
            elif source.startswith('{') and source.endswith('}'):
                special_key = source[1:-1]
                if special_key in ADDR_SOURCE_CODES:
                    signals["addr_source_key"] = special_key
                    signals["addr_out_bus_en"] = True
            elif source.startswith('*'):
                signals["mem_read_en"] = True
                signals["data_bus_in_en"] = True
                signals["addr_out_bus_en"] = True
                source_addr = source[1:]
                if source_addr.startswith('{') and source_addr.endswith('}'):
                    key = source_addr[1:-1]
                    if key == "0x00, adl":
                        signals["addr_source_key"] = "zeropage"
                    elif key == "latch":
                        signals["addr_source_key"] = "latch"
                    elif key == "adh, adl":
                        signals["addr_source_key"] = "latch"
                    elif key in ADDR_SOURCE_CODES:
                        signals["addr_source_key"] = key
                elif source_addr == "pc":
                    signals["addr_source_key"] = "pc"
                elif source_addr == "sp":
                    signals["addr_source_key"] = "stack"

            # 4. Analiza Celu (Dest)
            if dest:
                if dest in ["a", "x", "y", "sp", "p", "tmp", "ir", "adh", "adl"]:
                    signals[f"{'reg_' if dest not in ['tmp', 'ir', 'adh', 'adl', 'p'] else ''}{dest}_load_en"] = True
                elif dest == "pc":
                    signals["pc_load_en"] = True
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
                    if dest_addr.startswith('{') and dest_addr.endswith('}'):
                        key = dest_addr[1:-1]
                        if key == "0x00, adl":
                            signals["addr_source_key"] = "zeropage"
                        elif key == "latch":
                            signals["addr_source_key"] = "latch"
                        elif key in ADDR_SOURCE_CODES:
                            signals["addr_source_key"] = key
                    elif dest_addr == "sp":
                        signals["addr_source_key"] = "stack"

    # --- Złożenie słów ---
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

    w0 = ((1 if signals["p_b_force_one_en"] else 0) << 15 |
          (1 if signals["p_c_set_en"] else 0) << 14 |
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
#  SEKCJA 3: FUNKCJE POMOCNICZE (Z ZAPISEM DO FOLDERU)
# ==============================================================================
def translate_instruction(name: str, cycles: list):
    print(f"--- Mikrokod dla instrukcji: {name} ---")
    for i, cycle_code in enumerate(cycles):
        w2, w1, w0 = generate_microcode(cycle_code)
        print(f"Cykl {i}: {cycle_code:<55} -> W2={w2:04X}, W1={w1:04X}, W0={w0:04X}")
    print("-" * 80)


def generate_rom_files(microcode_map, num_opcodes=256, max_cycles=8):
    print(f"\n--- Generowanie plików tekstowych ROM w katalogu '{OUTPUT_DIR}' ---")

    # Upewnij się, że katalog istnieje
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

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

            roms_w2[cycle_index][opcode] = f"{w2:04X}"
            roms_w1[cycle_index][opcode] = f"{w1:04X}"
            roms_w0[cycle_index][opcode] = f"{w0:04X}"

    try:
        for i in range(num_banks):
            # Zapisz pliki w katalogu OUTPUT_DIR
            path_w2 = os.path.join(OUTPUT_DIR, f"w2_bank{i}.txt")
            path_w1 = os.path.join(OUTPUT_DIR, f"w1_bank{i}.txt")
            path_w0 = os.path.join(OUTPUT_DIR, f"w0_bank{i}.txt")

            with open(path_w2, "w") as f: f.write("\n".join(roms_w2[i]))
            with open(path_w1, "w") as f: f.write("\n".join(roms_w1[i]))
            with open(path_w0, "w") as f: f.write("\n".join(roms_w0[i]))

        print(f"Pomyślnie wygenerowano {num_banks * 3} plików tekstowych.")
    except IOError as e:
        print(f"Błąd podczas zapisu plików tekstowych: {e}")


def generate_csv_log(microcode_map):
    print(f"\n--- Generowanie logu CSV w katalogu '{OUTPUT_DIR}' ---")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    log_path = os.path.join(OUTPUT_DIR, "microcode_log.csv")

    try:
        with open(log_path, "w", newline="", encoding="utf-8") as f:
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
                        f"{w2:04X}", f"{w1:04X}", f"{w0:04X}"
                    ])
        print(f"Pomyślnie wygenerowano plik {log_path}")
    except IOError as e:
        print(f"Błąd podczas zapisu pliku CSV: {e}")


# ==============================================================================
#  SEKCJA 4: MAIN
# ==============================================================================
if __name__ == "__main__":
    print("--- Walidacja mapy mikrokodu ---")
    error_found = False
    for opcode, data in MICROCODE_MAP.items():
        mnemonic, addressing_mode, cycles = data
        if len(cycles) > 8:
            print(f"BŁĄD: {mnemonic} {addressing_mode} (Opcode {opcode:02X}) ma {len(cycles)} cykli!")
            error_found = True

    if not error_found:
        print("Walidacja długości cykli OK.")

        test_opcodes = [0xA9, 0x69, 0xBD, 0xF0, 0x4C]
        for op in test_opcodes:
            if op in MICROCODE_MAP:
                data = MICROCODE_MAP[op]
                translate_instruction(f"{data[0]} {data[1]}", data[2])

        generate_rom_files(MICROCODE_MAP)
        generate_csv_log(MICROCODE_MAP)
    else:
        print("Popraw błędy przed generowaniem plików.")