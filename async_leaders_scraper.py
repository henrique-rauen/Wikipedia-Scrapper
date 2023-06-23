import re
from bs4 import BeautifulSoup
import requests as r
import json
from httpx import AsyncClient
import asyncio
import time

#Apparently the bottleneck here is making the beautiful soup out of
#the entire wikipedia page. Putting it into an async function does
#not seem to help since async does not mean parallel, it still needs
#to not be processing something, just waiting. It only uses "idle"
#time to move on to another process, since beautifulsoup has no idle
#time, it has basically no gains. Only the webrequests offer gains
#but in this context they are far from being the bottleneck

async def make_soup(doc):
    return BeautifulSoup(doc, "html.parser")

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
    soup = await make_soup(page)
    for p in soup.find_all("p"):
        if len(p.find_all()) > 1 and len(p.find_all("b")) > 0:
            first_paragraph = await clean_up(p.text,
                                             clean_audio,
                                             clean_parenthesis,
                                             clean_spaces)
            print(first_paragraph)
            break
    return {id : first_paragraph}

async def clean_up(text, *patterns):
    for pat in patterns:
        tmp = re.sub(pat, "", text)
    return tmp


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
            responses = await asyncio.gather(*tasks)
            lead=[]
            for resp in responses:
                lead.append(resp)
    return lead

start = time.perf_counter()
asyncio.run(get_leaders())
end = time.perf_counter()
print("exec time: ", round(end - start, 2))
