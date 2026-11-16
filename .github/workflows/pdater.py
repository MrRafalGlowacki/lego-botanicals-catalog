import json
import re
import requests
from bs4 import BeautifulSoup

# Bazowa lista, którą już mamy w aplikacji
CATALOG_FILE = "catalog.json"

def fetch_and_merge():
    # Pobieranie istniejącej bazy z repozytorium lub tworzenie nowej
    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    except FileNotFoundError:
        catalog = []

    sets_map = {item["setNumber"]: item for item in catalog}

    # Pobieranie aktualnych danych z polskiego źródła
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    url = "https://promoklocki.pl/szukaj/?q=Botanical"
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("div[class*='box'], div[class*='item'], div[class*='product']")
        
        for item in items:
            title_elem = item.select_one("h2, h3, a[title]")
            if not title_elem:
                continue
            full_title = title_elem.get_text(strip=True)
            
            # Wyszukiwanie numeru zestawu
            number_match = re.search(r'\b(10\d{3}|11\d{3}|40\d{3})\b', full_title)
            if not number_match:
                continue
            set_num = number_match.group(1)
            
            clean_name = re.sub(r'^LEGO\s*\d+\s*', '', full_title, flags=re.IGNORECASE).strip()
            
            # Wyszukiwanie ceny PLN
            price_elem = item.select_one("[class*='price']")
            price_val = 0.0
            if price_elem:
                price_match = re.search(r'(\d+[\d\s]*[,.]\d{2})', price_elem.get_text())
                if price_match:
                    price_val = float(price_match.group(1).replace(" ", "").replace(",", "." architecture))
            
            if set_num not in sets_map:
                sets_map[set_num] = {
                    "setNumber": set_num,
                    "namePl": clean_name if clean_name else f"Zestaw {set_num}",
                    "category": "Nowości",
                    "releaseDate": "Nowość",
                    "retirementDate": None,
                    "catalogPricePln": price_val,
                    "isOwned": False
                }
            else:
                # Aktualizacja ceny jeśli dostępna
                if price_val > 0:
                    sets_map[set_num]["catalogPricePln"] = price_val

    # Zapis zaktualizowanego pliku
    updated_list = list(sets_map.values())
    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_list, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_and_merge()
