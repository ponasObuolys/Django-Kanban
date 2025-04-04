#!/bin/bash

# Nustatomos spalvos išvesties formatavimui
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Django vertimų taisymo įrankis serveryje${NC}"
echo "======================================"

# 1. Patikrinama ar įdiegtas gettext
echo -e "${YELLOW}1. Tikrinam, ar gettext įdiegtas${NC}"
if ! command -v msgfmt &> /dev/null; then
    echo -e "${RED}Nerastas msgfmt! Diegimas...${NC}"
    sudo apt-get update && sudo apt-get install -y gettext
else
    echo -e "${GREEN}gettext jau įdiegtas.${NC}"
fi

# 2. Patikrinam lokalės konfigūraciją
echo -e "\n${YELLOW}2. Patikrinam lokalės konfigūraciją${NC}"
locale -a | grep lt_LT
if [ $? -ne 0 ]; then
    echo -e "${RED}Nerasta lt_LT lokalė. Įdiegimas...${NC}"
    sudo locale-gen lt_LT.UTF-8
    sudo update-locale
else
    echo -e "${GREEN}lt_LT lokalė jau įdiegta.${NC}"
fi

# 3. Patikrinam vertimų statusą
echo -e "\n${YELLOW}3. Patikrinam vertimų būseną${NC}"
python check_locale_settings.py

# 4. Kompiliuojam vertimus
echo -e "\n${YELLOW}4. Kompiliuojam vertimus${NC}"
python manage.py compilemessages
echo -e "${GREEN}Vertimų kompiliavimas baigtas.${NC}"

# 5. Nustatom teisingas teises
echo -e "\n${YELLOW}5. Nustatom teisingas teises failams${NC}"
chmod -R 644 locale/*/LC_MESSAGES/*.mo
echo -e "${GREEN}Teisės nustatytos.${NC}"

# 6. Perkraunam Django aplikaciją
echo -e "\n${YELLOW}6. Ar norite perkrauti Django aplikaciją? (y/n)${NC}"
read answer
if [ "$answer" = "y" ]; then
    # Pakeiskite žemiau esančią komandą pagal jūsų serverio konfigūraciją
    echo "Paleidžiama perkrovimo komanda..."
    sudo systemctl restart nginx
    sudo systemctl restart gunicorn
    echo -e "${GREEN}Django aplikacija perkrauta.${NC}"
else
    echo -e "${YELLOW}Perkrovimas praleistas.${NC}"
fi

echo -e "\n${GREEN}Viskas atlikta! Dabar pabandykite pakeisti kalbą savo aplikacijoje.${NC}" 