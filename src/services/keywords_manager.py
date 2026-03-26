# keywords_manager.py

import time
import requests
import json
import html
from bs4 import BeautifulSoup

from src.services.database import Database
from .excel import Excel

class KeywordsManager:
    def __init__(self, row_range: str, words_index: int, database: 'Database'):
        self.row_range = row_range
        self.words_index = words_index
        self.database = database
        self.excel = Excel()
    

    def homepage(self, keyword: str, api, url: str) -> tuple[bool, list[str]]:
        url = url.format(keyword=keyword)
        r_list: list[str] = []
        
        while True:
            time.sleep(0.2)
            try:
                response = requests.get(url)
                # response = requests.get(
                #     url='https://proxy.scrapeops.io/v1/',
                #     params={
                #         'api_key': f'{api}',
                #         'url': f'{url}', 
                #     },
                # )
                if response.status_code == 200:
                    decoded_response = response.text

                    cleaned_response = decoded_response.replace(")]}'", "")

                    try:
                        json_data = json.loads(cleaned_response)

                        suggestions = json_data[0]
                        for index, suggestion in enumerate(suggestions):
                            cleaned_suggestion = html.unescape(suggestion[0])
                            print(f"[{index+1}] {cleaned_suggestion}")
                            r_list.append(cleaned_suggestion)
                            
                        return True, r_list
                    except json.JSONDecodeError:
                        print("Error parsing the JSON data.")
                else:
                    print(f"Request failed with status code: {response.status_code} and retrying")
                    time.sleep(10)
            except:
                pass
    def inside_page(self, keyword: str, api, url: str) -> tuple[bool, list[str]]:
        url = url.format(keyword=keyword)
        r_list: list[str] = []
        
        while True:
            time.sleep(0.2)
            try:
                response = requests.get(url)
                # response = requests.get(
                #     url='https://proxy.scrapeops.io/v1/',
                #     params={
                #         'api_key': f'{api}',
                #         'url': f'{url}', 
                #     },
                # )

                if response.status_code == 200:
                    decoded_response = response.text

                    cleaned_response = decoded_response.replace(")]}'", "")

                    try:
                        json_data = json.loads(cleaned_response)

                        suggestions = json_data[0]  
                        for index, suggestion in enumerate(suggestions):
                            cleaned_suggestion = html.unescape(suggestion[0])
                            print(f"[{index+1}] {cleaned_suggestion}")
                            r_list.append(cleaned_suggestion)
                        return True, r_list
                    except json.JSONDecodeError:
                        print("Error parsing the JSON data.")
                else:
                    print(f"Request failed with status code: {response.status_code} and retrying")
                    time.sleep(10)
            except:
                pass
    def related_bottom(self, keyword: str, api, url: str) -> tuple[bool, list[str]]:
        url = url.format(keyword=keyword)
        r_list: list[str] = []
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        logo_not_found_count = 0
        logo_not_found_limit = 10
        while True:
            time.sleep(0.2)
            try:
                response = requests.get(
                    url='https://proxy.scrapeops.io/v1/',
                    params={
                        'api_key': f'{api}',
                        'url': f'{url}', 
                    },
                )
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    sugg_elements = soup.find_all("span", class_="Xe4YD")
                    sugg_elements2 = soup.find_all("div", {"class": "b2Rnsc vIifob"})
                    logo_element = soup.find(id="logo")
                    
                    
                    if sugg_elements:
                        print("Element Num 1 Found")
                        for index, span in enumerate(sugg_elements):
                            div_element = span.find("div")
                            if div_element:
                                text = div_element.get_text().replace("\n", "")
                                print(f"[{index+1}] {text}")
                                r_list.append(text)
                        return True, r_list
                    
                    elif sugg_elements2:
                        print("Element Num 2 Found")
                        if sugg_elements2:
                            for index, element in enumerate(sugg_elements2):
                                text2 = element.get_text().replace("\n", "")
                                print(f"[{index+1}] {text2}")
                                r_list.append(text2)
                        return True, r_list
                    else:
                        if not logo_element:
                            logo_not_found_count += 1
                            if logo_not_found_count >= logo_not_found_limit:
                                print("Logo element not found. Page may not have loaded correctly....exiting")
                                break
                            print("Logo element not found. Page may not have loaded correctly....retring")
                            time.sleep(10)
                            continue
                        print("Target element not found.")
                        with open(f"fails/{keyword}.html", "w", encoding="utf-8") as file:
                            file.write(response.text)
                        return False, r_list
                        
                else:
                    print(f"Request failed with status code: {response.status_code}")
                    time.sleep(10)
            except Exception as e:
                pass