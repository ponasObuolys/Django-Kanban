#!/bin/bash

# Spalvų nustatymai
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Django vertimų diegimas serveryje${NC}"
echo "===================================="

# 1. Įdiegti gettext (jei reikia)
echo -e "${YELLOW}1. Tikrinama, ar įdiegtas gettext${NC}"
if ! command -v msgfmt &> /dev/null; then
    echo -e "${RED}gettext nerastas. Diegiama...${NC}"
    sudo apt-get update && sudo apt-get install -y gettext
    echo -e "${GREEN}gettext įdiegtas${NC}"
else
    echo -e "${GREEN}gettext jau įdiegtas${NC}"
fi

# 2. Įdiegti lietuvių kalbos lokalę (jei reikia)
echo -e "\n${YELLOW}2. Tikrinama, ar įdiegta lietuvių lokalė${NC}"
if ! locale -a | grep -q lt_LT; then
    echo -e "${RED}Lietuvių lokalė nerasta. Diegiama...${NC}"
    sudo locale-gen lt_LT.UTF-8
    sudo update-locale
    echo -e "${GREEN}Lietuvių lokalė įdiegta${NC}"
else
    echo -e "${GREEN}Lietuvių lokalė jau įdiegta${NC}"
fi

# 3. Sukompiliuoti vertimus su Django komanda
echo -e "\n${YELLOW}3. Kompiliuojami vertimai${NC}"
python3 -m pip install polib
python3 convert_po_to_mo.py
echo -e "${GREEN}Vertimai sukompiliuoti${NC}"

# 4. Perkrauti Django aplikaciją
echo -e "\n${YELLOW}4. Ar norite perkrauti Django aplikaciją? (t/n)${NC}"
read answer
if [ "$answer" = "t" ] || [ "$answer" = "T" ]; then
    echo "Perkraunama Django aplikacija..."
    
    # Pakeiskite šias komandas pagal jūsų serverio konfigūraciją
    sudo systemctl restart gunicorn
    sudo systemctl restart nginx
    
    echo -e "${GREEN}Django aplikacija perkrauta${NC}"
else
    echo -e "${YELLOW}Perkrovimas praleistas${NC}"
    echo -e "Nepamirškite vėliau perkrauti Django aplikaciją komandomis:"
    echo "sudo systemctl restart gunicorn"
    echo "sudo systemctl restart nginx"
fi

echo -e "\n${GREEN}Vertimai sėkmingai įdiegti!${NC}"
echo -e "${YELLOW}Dabar galite naudoti lietuvių kalbą savo aplikacijoje.${NC}" 