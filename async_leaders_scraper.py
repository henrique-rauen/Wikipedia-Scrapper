import re
from bs4 import BeautifulSoup
import requests as r
import json
from httpx import AsyncClient
import asyncio

async def get_first_paragraph(wikipedia_url, session):
    """Returns the first paragraph of a given wikipedia_url.
    The return is cleaned from wikipedia related strings, like
    pronounciation strings and notes. Returns None if no paragraph
    is found"""
    audio_pattern = (r"(?:/.+?;)|(?:/.+?/)|(?:;*\[.*?[\];])|(?:Écouter)"
                      "|(?:\(info.*?\))|(?:uitspraak)")
    clean_audio = re.compile(audio_pattern)
    clean_parenthesis = re.compile(r"[(]\s*[)]")
    clean_spaces = re.compile(r"(?:(?<=[\(\s])\s)|(?:\s(?=[,]))")
    first_paragraph = None
    page = await session.get(wikipedia_url)
    soup =  BeautifulSoup(page, "html.parser")
    for p in soup.find_all("p"):
        if len(p.find_all()) > 1 and len(p.find_all("b")) > 0:
            tmp = re.sub(clean_audio, "", p.text)
            tmp = re.sub(clean_parenthesis, "", tmp)
            first_paragraph = re.sub(clean_spaces, "", tmp)
            print(first_paragraph)
            break
    return first_paragraph

async def get_leaders():
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
        tasks = []
        async with AsyncClient() as async_session:
            for c in countries:
                leaders_per_country[c] = session.get(leaders_url + "?country="
                                                                     + c,
                                                cookies=cookies).json()
                for l in leaders_per_country[c]:
                    tasks.append(asyncio.create_task(
                                    get_first_paragraph(l["wikipedia_url"],
                                                    async_session)
                                                    )
                                )
                    """
                    l["short_intro"] = get_first_paragraph(l["wikipedia_url"],
                                                            session)
                    print(l["first_name"], l["last_name"])
                    print(l["short_intro"])
    """
            responses = await asyncio.gather(*tasks)
    #return leaders_per_country

def save(data, file= 'leaders.json'):
    """Turns 'data' into a json object and write it to 'file'"""
    with open(file,"w") as write_file:
        json.dump(data, write_file)

#save(get_leaders())
asyncio.run(get_leaders())
