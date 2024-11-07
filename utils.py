# utils.py

import requests
from bs4 import BeautifulSoup
import re
import json

def clean_text(text):

    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'/[^;]*;', '', text)
    text = re.sub(r'[ⓘ]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\(/\s*[^)]*\)', '', text)
    text = re.sub(r'\(\s+', '(', text)
    
    return text.strip()

def get_first_paragraph(wikipedia_url, session):

    content = session.get(wikipedia_url)
    soup = BeautifulSoup(content.text, 'html.parser')
    paragraphs = soup.find_all('p')

    for paragraph in paragraphs[1:]:
        paragraph_text = paragraph.get_text()
        if re.search(r'\d', paragraph_text):
            return clean_text(paragraph_text)

def get_leaders():
    url = "https://country-leaders.onrender.com"
    cookies_url = url + "/cookie"
    countries_url = url + "/countries"
    leaders_url = url + "/leaders"
    
    cookies_req = requests.get(cookies_url)
    cookies = cookies_req.cookies.get_dict()
    
    countries_req = requests.get(countries_url, cookies=cookies)
    countries = countries_req.json()

    leaders_per_country = {}
    
    with requests.Session() as session:
        for country in countries:
            leaders_req = session.get(leaders_url, params={'country': country}, cookies=cookies)
            leaders = leaders_req.json()
            leaders_per_country[country] = leaders

        leaders_dict = {}
        for country_code, leaders in leaders_per_country.items():
            for leader in leaders:
                leader_name = f"{leader['first_name']} {leader['last_name']}"
                first_paragraph = get_first_paragraph(leader['wikipedia_url'], session)
                leaders_dict[leader_name] = first_paragraph

    return leaders_dict

def save(dict_as_json, file_name):
    with open(file_name, 'w') as f:
        json.dump(dict_as_json, f)

def load(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)