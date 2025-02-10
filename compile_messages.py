import os
import subprocess

msgfmt_path = r'C:\Program Files\gettext-iconv\bin\msgfmt.exe'
po_file = 'locale/lt/LC_MESSAGES/django.po'
mo_file = 'locale/lt/LC_MESSAGES/django.mo'

try:
    subprocess.run([msgfmt_path, po_file, '-o', mo_file], check=True)
    print("Successfully compiled messages")
except subprocess.CalledProcessError as e:
    print(f"Error compiling messages: {e}")
except Exception as e:
    print(f"Unexpected error: {e}") 