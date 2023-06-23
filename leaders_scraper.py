#! /usr/bin/python

#Created by Henrique Rauen (rickgithub@hsj.email)
#Last Modified: 2023-06-23 09:37
import re
from bs4 import BeautifulSoup
import requests as r
import json
import time

def get_text(url, session = None):
    """Returns the webpage contents of a url. If no session is added,
    use default requests.get() """
    if session:
        return session.get(url).text
    else:
        return r.get(url).text

def get_first_paragraph(wikipedia_url, session=None):
    """Returns the first paragraph of a given wikipedia_url. If session
    is not specified, uses requests.get(), otherwise uses the session.
    The return is cleaned from wikipedia related strings, like
    pronounciation strings and notes. Returns None if no paragraph
    is found"""
    #print(wikipedia_url)
    audio_pattern = (r"(?:/.+?;)|(?:/.+?/)|(?:;*\[.*?[\];])|(?:Écouter)"
                      "|(?:\(info.*?\))|(?:uitspraak)")
    clean_audio = re.compile(audio_pattern)
    clean_parenthesis = re.compile(r"[(]\s*[)]")
    clean_spaces = re.compile(r"(?:(?<=[\(\s])\s)|(?:\s(?=[,]))")
    first_paragraph = None
    page = get_text(wikipedia_url, session)
    soup =  BeautifulSoup(page, "html.parser")
    for p in soup.find_all("p"):
        if len(p.find_all()) > 1 and len(p.find_all("b")) > 0:
            tmp = re.sub(clean_audio, "", p.text)
            tmp = re.sub(clean_parenthesis, "", tmp)
            first_paragraph = re.sub(clean_spaces, "", tmp)
            break
    return first_paragraph

def get_leaders():
    """Uses the 'country-leaders' API to create a dict object with the
    following content:
    dict {country = [leader1,leader2...]}
    where leaderN is a dict object in the following format:
    dict leaderN = {id, first_name, last_name, birth_date, death_date,
    place_of_birth, wikipedia_url, start_mandate, end_mandate,
    short_intro}. All of those keys have strings as values."""
    root_url = "https://country-leaders.onrender.com"
    countries_url = root_url + "/countries"
    cookie_url = root_url + "/cookie"
    leaders_url = root_url + "/leaders"
    leaders_per_country = {}
    with r.Session() as session:
        cookies = session.get(cookie_url).cookies
        countries = session.get(countries_url, cookies=cookies).json()
        for c in countries:
            req_result = session.get(leaders_url + "?country=" + c,
                                    cookies=cookies)
            if req_result.status_code!=200: #Cookie error
                cookies = session.get(cookie_url).cookies
                req_result = session.get(leaders_url + "?country=" + c,
                                        cookies=cookies)
            leaders_per_country[c] = req_result.json()
            for l in leaders_per_country[c]:
                l["short_intro"] = get_first_paragraph(l["wikipedia_url"],
                                                        session)
                print(l["first_name"], l["last_name"])
                print(l["short_intro"])
    return leaders_per_country

def save(data, file= 'leaders.json'):
    """Turns 'data' into a json object and write it to 'file'"""
    with open(file,"w") as write_file:
        json.dump(data, write_file)

save(get_leaders())
