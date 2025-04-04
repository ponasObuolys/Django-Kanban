#!/usr/bin/env python
import os
import sys
import locale
import subprocess
import django
from django.conf import settings

# Nustatome, kad būtų galima naudoti Django nustatymus
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_project.settings')
django.setup()

def check_locale_settings():
    """Patikrina lokalės nustatymus sistemoje ir Django projekte"""
    print("=== Sistemos lokalės informacija ===")
    print(f"Dabartinė lokalė: {locale.getlocale()}")
    print(f"Prieinamos lokalės: {locale.locale_alias}")
    
    print("\n=== Django kalbos nustatymai ===")
    print(f"LANGUAGE_CODE: {settings.LANGUAGE_CODE}")
    print(f"LANGUAGES: {settings.LANGUAGES}")
    print(f"LOCALE_PATHS: {settings.LOCALE_PATHS}")
    print(f"USE_I18N: {settings.USE_I18N}")
    print(f"USE_L10N: {settings.USE_L10N}")
    
    print("\n=== Vertimų failai ===")
    for lang_code, lang_name in settings.LANGUAGES:
        po_path = os.path.join(settings.LOCALE_PATHS[0], lang_code, 'LC_MESSAGES', 'django.po')
        mo_path = os.path.join(settings.LOCALE_PATHS[0], lang_code, 'LC_MESSAGES', 'django.mo')
        
        print(f"Kalba: {lang_name} ({lang_code})")
        print(f"  PO failas: {'Egzistuoja' if os.path.exists(po_path) else 'NERASTAS!'}")
        print(f"  MO failas: {'Egzistuoja' if os.path.exists(mo_path) else 'NERASTAS!'}")
        
        if os.path.exists(mo_path):
            # Patikriname MO failo teises
            stat_info = os.stat(mo_path)
            print(f"  MO failo teisės: {stat_info.st_mode}")
    
def compile_messages():
    """Kompiliuoja vertimų failus"""
    print("\n=== Kompiliuojami vertimų failai ===")
    try:
        # Patikriname, ar įdiegtas gettext
        subprocess.run(['msgfmt', '--version'], check=True, capture_output=True)
        
        # Kompiliuojame visas kalbas
        for lang_code, lang_name in settings.LANGUAGES:
            po_path = os.path.join(settings.LOCALE_PATHS[0], lang_code, 'LC_MESSAGES', 'django.po')
            mo_path = os.path.join(settings.LOCALE_PATHS[0], lang_code, 'LC_MESSAGES', 'django.mo')
            
            if os.path.exists(po_path):
                print(f"Kompiliuojama {lang_code}...")
                subprocess.run(['msgfmt', po_path, '-o', mo_path], check=True)
                print(f"  Sėkmingai sukompiliuotas {mo_path}")
            else:
                print(f"  Trūksta PO failo: {po_path}")
        
        print("\nVisi vertimai sėkmingai sukompiliuoti.")
    except subprocess.CalledProcessError as e:
        print(f"Klaida vykdant msgfmt: {e}")
    except Exception as e:
        print(f"Netikėta klaida: {e}")

if __name__ == "__main__":
    check_locale_settings()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--compile":
        compile_messages()
    else:
        print("\nNorėdami sukompiliuoti vertimus, naudokite parametrą --compile") 