import requests
from bs4 import BeautifulSoup
import re
import time
from tqdm import tqdm
import json

class Scraper:
    def __init__(self):
        self.url = "https://pocket.limitlesstcg.com/cards"
        self.soup = BeautifulSoup(requests.get(self.url).text, "html.parser")
        self.card_sets = {}
        self.card_dict_list = []

    def scrape_card_sets(self):
        sets = self.soup.find("table", class_="data-table").find_all("tr")[2:]
        for set in tqdm(sets, desc="Scraping card sets"):
            set_code = set.find("a")["href"].split("/")[-1]
            set_name = set.find_all("td")[0].text.strip().split("\n")[0]
            set_release_date = set.find_all("td")[1].text.strip()
            set_total_cards = set.find_all("td")[2].text.strip()
            self.card_sets[set_code] = {
                "name": set_name,
                "release_date": set_release_date,
                "total_cards": set_total_cards
            }
        return self.card_sets

    def scrape_card(self, set_code, card_no):
        url_card = f"{self.url}/{set_code}/{card_no}"

        response = requests.get(url_card)
        soup = BeautifulSoup(response.text, "html.parser")

        card_dict = {}

        # card number
        card_dict["set_code"] = set_code
        card_dict["card_number"] = card_no

        _card_type = soup.find("p", class_="card-text-type").text.strip().split(" - ")
        _card_type = [a.strip() for a in _card_type]
        card_type = _card_type[0]
        card_dict["name"] = soup.find("span", class_="card-text-name").text

        image_url = soup.find("div", class_="card-image").find("img")["src"]
        card_dict["image_url"] = image_url

        if card_type == "Pokémon":
            _name_type_hp = soup.find("p", class_="card-text-title").find_all(string=True, recursive=True)
            _name_type_hp = [i.strip() for i in _name_type_hp]
            _name_type_hp = "".join(_name_type_hp)
            _name_type_hp = _name_type_hp.split("-")
            _name_type_hp = [i.strip() for i in _name_type_hp]
            card_dict["pkmn_type"] = _name_type_hp[1]
            card_dict["pkmn_hp"] = _name_type_hp[2]

            # stage
            card_dict["stage"] = _card_type[1]
            if card_dict["stage"] != "Basic":
                card_dict["evolves_from"] = _card_type[2].split("\n")[1].strip()
            
            # card ability
            _ability = soup.find("p", class_="card-text-ability-info")
            if _ability:
                card_dict["ability"] = {}
                ability_name = _ability.string.replace("Ability: ", "").strip()
                ability_effect = soup.find("p", class_="card-text-ability-effect").find_all(string=True, recursive=False)
                ability_effect = [i.strip() for i in ability_effect]
                ability_effect = "".join(ability_effect).strip()
                card_dict["ability"][ability_name] = ability_effect

            # card attacks
            _attacks = soup.find_all("div", class_="card-text-attack")
            card_dict["attacks"] = {}
            for _attack in _attacks:
                _info = _attack.find("p", class_="card-text-attack-info").find_all(string=True, recursive=False)
                _info = [i.strip() for i in _info]
                _info = "".join(_info).strip()
                _match = re.search(r'(.*?)(\d+[+x]{0,1})?$', _info)
                if _match:
                    attack_name = _match.group(1).strip()
                    card_dict["attacks"][attack_name] = {}
                    
                    energy_cost = _attack.find("p", class_="card-text-attack-info").find("span", class_="ptcg-symbol").string
                    card_dict["attacks"][attack_name]["energy_cost"] = energy_cost

                    attack_effect = _attack.find("p", class_="card-text-attack-effect").find_all(string=True, recursive=False)
                    attack_effect = [i.strip() for i in attack_effect]
                    attack_effect = "".join(attack_effect).strip()
                    if attack_effect:
                        card_dict["attacks"][attack_name]["effect"] = attack_effect

                    if _match.group(2):
                        damage = _match.group(2).strip()
                        card_dict["attacks"][attack_name]["damage"] = damage

            # weakness and retreat cost
            _wrr = soup.find("p", class_="card-text-wrr").find_all(string=True)
            card_dict["weakness"] = _wrr[0].replace("Weakness: ", "").strip()
            card_dict["retreat_cost"] = _wrr[1].replace("Retreat: ", "").strip()


            # card text flavor
            if soup.find("div", class_="card-text-section card-text-flavor"):
                card_dict["flavor"] = soup.find("div", class_="card-text-section card-text-flavor").string.strip()

        elif card_type == "Trainer":
            _card_type_detail = _card_type[1].strip()
            card_dict["trainer_type"] = _card_type_detail

            # card text
            _card_text_ls = soup.find_all("div", class_="card-text-section")
            if len(_card_text_ls) > 1:
                card_text = _card_text_ls[1].text.strip()
                card_dict["text"] = card_text

        # artist
        card_dict["artist"] = soup.find("div", class_="card-text-section card-text-artist").select('a')[0].string.strip()

        # rarity
        card_rarity =soup.find("div", class_="prints-current-details").find_all("span")[1].text.strip().split("·")[1].strip()
        card_dict["rarity"] = card_rarity

        # other versions
        _other_versions = soup.find("table", class_="card-prints-versions").find_all("tr")[1:]
        if _other_versions:
            card_dict["other_versions"] = {}
            for _version in _other_versions:
                is_current_version = False if _version.get('class') and _version.get('class')[0] == "current" else True
                if is_current_version:
                    version_set_code = _version.find("a").get('href').split("/")[-2]
                    version_card_no = _version.find("a").get('href').split("/")[-1]
                    card_dict["other_versions"]["set_code"] = version_set_code
                    card_dict["other_versions"]["card_number"] = version_card_no

        self.card_dict_list.append(card_dict)
        return card_dict

    def scrape_all_cards_for_card_set(self, set_code):
        if not self.card_sets:
            self.scrape_card_sets()

        if set_code not in self.card_sets:
            print(f"Set {set_code} not found")
            return

        set_total_cards = int(self.card_sets[set_code]["total_cards"])
        for card_no in tqdm(range(1, set_total_cards+1), desc=f"Scraping cards for set {set_code}"):
            card_dict = self.scrape_card(set_code, card_no)
        
    def scrape_all_cards(self):
        if not self.card_sets:
            self.scrape_card_sets()

        for set_code in tqdm(self.card_sets, desc="Scraping all cards"):
            self.scrape_all_cards_for_card_set(set_code)
        
if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_all_cards()
    with open("card_dict_list.json", "w") as f:
        json.dump(scraper.card_dict_list, f)
    with open("card_sets.json", "w") as f:
        json.dump(scraper.card_sets, f)
    
    print("Scraping complete")
