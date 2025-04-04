#!/usr/bin/env python
import os
import subprocess

# Pašalinu Windows kelią ir naudoju universalų būdą surasti msgfmt
# msgfmt_path = r'C:\Program Files\gettext-iconv\bin\msgfmt.exe'
po_file = 'locale/lt/LC_MESSAGES/django.po'
mo_file = 'locale/lt/LC_MESSAGES/django.mo'

try:
    # Linux/Ubuntu sistemose msgfmt paprastai yra PATH kintamajame
    subprocess.run(['msgfmt', po_file, '-o', mo_file], check=True)
    print("Sėkmingai sukompiliuoti vertimai")
except subprocess.CalledProcessError as e:
    print(f"Klaida kompiliuojant vertimus: {e}")
except Exception as e:
    print(f"Netikėta klaida: {e}") 