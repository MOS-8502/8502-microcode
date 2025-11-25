# burner.py
# -*- coding: utf-8 -*-

import json
import os
import re

# ==============================================================================
#  KONFIGURACJA
# ==============================================================================

# UWAGA: Ścieżka względna do PLA.json, zakładająca, że 'burner.py' jest
# uruchamiany z katalogu nadrzędnego dla 'MOS8502-dls-core'.
PLA_FILE = os.path.join("..", "MOS8502-dls-core", "dls", "Chips", "PLA.json")
BUILD_DIR = "build"


def inject_rom_data_to_pla():
    """
    Wczytuje skompilowane pliki wsadów z katalogu BUILD_DIR (wYbX.txt)
    i aktualizuje komponenty ROM w PLA.json na podstawie ich etykiet (wYbX).
    """

    print("\n--- URUCHAMIANIE WIRTUALNEJ WYPALARKI ROM (PLA INJECTION) ---")

    try:
        # Wczytaj PLA.json
        with open(PLA_FILE, 'r', encoding='utf-8') as f:
            pla_data = json.load(f)
    except Exception as e:
        print(f"❌ BŁĄD: Nie można wczytać pliku {PLA_FILE}. Sprawdź ścieżkę: {os.path.abspath(PLA_FILE)}. Detale: {e}")
        return

    # Jeśli katalog build nie istnieje, przerywamy
    if not os.path.isdir(BUILD_DIR):
        print(f"❌ BŁĄD: Nie znaleziono katalogu {BUILD_DIR}. Uruchom najpierw ucode.py.")
        return

    rom_files = os.listdir(BUILD_DIR)
    injected_count = 0

    # 1. Tworzenie mapy etykiet dla szybkiego dostępu
    component_map = {}
    for component in pla_data.get("SubChips", []):
        label = component.get("Label", "")
        if label:
            component_map[label] = component

    # Lista wszystkich 24 oczekiwanych etykiet dla weryfikacji (w0..w2 x b0..b7)
    expected_labels = {f'w{y}b{x}' for y in range(3) for x in range(8)}
    found_labels = set()

    # 2. Iteruj przez pliki w katalogu 'build'
    for filename in rom_files:
        # Regex dopasowuje w[cyfra]b[cyfra].rom
        match = re.match(r'(w\d+b\d+)\.rom$', filename)

        if match:
            # Etykieta to część nazwy pliku BEZ rozszerzenia '.txt'
            component_label_to_match = match.group(1)

            if component_label_to_match in component_map:
                txt_path = os.path.join(BUILD_DIR, filename)
                component = component_map[component_label_to_match]

                try:
                    # 3. Wczytaj zawartość pliku TXT (HEX -> INT)
                    with open(txt_path, 'r') as f:
                        hex_values = [line.strip() for line in f if line.strip()]
                        # Konwersja na INT z bazy 16 (HEX)
                        int_data = [int(v, 16) for v in hex_values]

                    # 4. Wstrzyknij dane do InternalData (przepalanie)
                    component["InternalData"] = int_data
                    print(f"✅ SUCCESS: Przepalono '{component_label_to_match}' (plik: {filename}).")
                    injected_count += 1
                    found_labels.add(component_label_to_match)

                except Exception as e:
                    print(f"❌ BŁĄD PRZY ZAPISIE DANYCH dla etykiety '{component_label_to_match}': {e}")
            else:
                print(
                    f"⚠️ OSTRZEŻENIE: Nie znaleziono KOMPONENTU z etykietą '{component_label_to_match}' w {PLA_FILE}. Pominięto.")

    # 5. Weryfikacja i Zapis
    missing_labels = expected_labels - found_labels
    if missing_labels:
        print(f"\n🛑 UWAGA: Wstrzyknięto dane tylko do {injected_count}/{len(expected_labels)} ROM-ów.")
        print(
            f"   BRAKUJĄCE ETYKIETY (sprawdź {PLA_FILE} lub folder {BUILD_DIR}): {', '.join(sorted(list(missing_labels)))}")

    if injected_count > 0:
        try:
            with open(PLA_FILE, 'w', encoding='utf-8') as f:
                # Używamy indent=2 dla lepszej czytelności w DLS
                json.dump(pla_data, f, indent=2)
            print(f"\n--- ZAPISANO NOWY {PLA_FILE} pomyślnie. ---\n")
        except Exception as e:
            print(f"❌ BŁĄD: Nie można zapisać pliku {PLA_FILE}: {e}")
    else:
        print("\n--- NIE ZNALEZIONO PASUJĄCYCH PLIKÓW MIKROKODU DO WSTRZYKNIĘCIA. --- \n")


if __name__ == "__main__":
    inject_rom_data_to_pla()