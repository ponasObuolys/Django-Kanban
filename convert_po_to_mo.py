#!/usr/bin/env python3
import polib
import os

def convert_po_to_mo(po_file_path, mo_file_path):
    """Konvertuoja .po failą į .mo failą naudojant polib biblioteką"""
    print(f"Konvertuojama: {po_file_path} -> {mo_file_path}")
    po = polib.pofile(po_file_path)
    po.save_as_mofile(mo_file_path)
    print(f"Sėkmingai sukurtas: {mo_file_path}")

def process_locale_dir(locale_dir="locale"):
    """Apdoroja visus .po failus nurodytame kataloge ir paverčia juos į .mo failus"""
    base_dir = os.path.abspath(os.path.dirname(__file__))
    locale_path = os.path.join(base_dir, locale_dir)
    
    if not os.path.exists(locale_path):
        print(f"Klaida: katalogas '{locale_path}' nerastas")
        return
    
    for root, dirs, files in os.walk(locale_path):
        for file in files:
            if file.endswith('.po'):
                po_file_path = os.path.join(root, file)
                mo_file_path = po_file_path.replace('.po', '.mo')
                convert_po_to_mo(po_file_path, mo_file_path)

if __name__ == "__main__":
    try:
        # Pirma patikrinkime, ar polib įdiegtas
        import polib
    except ImportError:
        print("Trūksta polib bibliotekos. Diegiama...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "polib"])
        print("polib įdiegtas sėkmingai.")
    
    process_locale_dir()
    print("Vertimų kompiliavimas baigtas sėkmingai!") 