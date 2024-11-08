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

def get_leader_birth_year(paragraphs, leader_birth_date)  :

        if leader_birth_date != None :
                        leader_birth_year = leader_birth_date[:4]
                        return leader_birth_year


        else :

                for para in paragraphs :
                        match = re.search(r'[0-9]{4}', para.text)
                        if match:
                                leader_birth_year = match.group()
                                return leader_birth_year
                        
def get_first_paragraph(wikipedia_url, session, leader_birth_date):
    content = session.get(wikipedia_url)
    soup = BeautifulSoup(content.text, 'html.parser')
    paragraphs = soup.find_all('p')

    leader_birth_year = get_leader_birth_year(paragraphs, leader_birth_date)

    for paragraph in paragraphs[1:]:
        paragraph_text = paragraph.get_text()
        if re.search(r'\d', paragraph_text):
            return clean_text(paragraph_text), leader_birth_year

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
                first_paragraph, leader_birth_year = get_first_paragraph(
                    leader['wikipedia_url'], session, leader['birth_date']
                )
                leaders_dict[leader_name] = {
                    'paragraph': first_paragraph,
                    'birth_year': leader_birth_year
                }
    return leaders_dict

def save(dict_as_json, file_name):
    with open(file_name, 'w') as f:
        json.dump(dict_as_json, f)

def load(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)
