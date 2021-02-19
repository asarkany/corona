import csv
import time
from random import random

from bs4 import BeautifulSoup
import pandas as pd
import requests

class NoAuthors(Exception):
    pass

class NoneExists(Exception):
    pass

class MoreThanOneExists(Exception):
    pass

def find_only_methodfactory(bs4tag):
    def function(*args, **kwargs):
        return find_only(bs4tag, *args, **kwargs)
    return function

def find_only(bs4tag, *args, **kwargs):
    find_result = bs4tag.find_all(*args, **kwargs)
    if len(find_result) == 0:
        raise NoneExists()
    elif len(find_result) > 1:
        raise MoreThanOneExists(f"{len(find_result)} tags were retrieved")

    ret_object = find_result[0]
    setattr(ret_object,"find_only",find_only_methodfactory(ret_object))
    return ret_object

def wait():
    time.sleep(random() * 3)

def scrape_wikipedia():
    print("Scraping wikipedia...")
    wait()
    url = "https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Hungary"
    page_source = requests.get(url).content

    html = BeautifulSoup(page_source, "lxml")

    table = find_only(html,"div",{"class":"barbox tright"}).find_only("table").tbody
    rows = filter(lambda tr: "class" in tr.attrs and "mw-collapsible" in tr.attrs["class"]  ,
                table.find_all("tr"))
    rows = list(rows)

    wikidata_df = pd.DataFrame([], columns=["date","death_all"])
    for ri, row in enumerate(rows):
        cellgroups = list(row.find_all("td", recursive=False))
        datum = cellgroups[0].text
        total_deaths_str = cellgroups[3].find_all("span")[0].text.replace(",","")
        total_deaths = int(total_deaths_str) if total_deaths_str != '' else 0
        wikidata_df.loc[ri] = [datum, total_deaths]

    wikidata_df.to_csv("wikidata.csv", index=False)

def scrape_govhu():
    print("Scraping koronavirus.gov.hu...")
    print("Page:")
    raw_data = []
    no_more_page = False
    page = 0
    while not no_more_page:
        if page % 10 == 0:
            print(f"{page}...")
        wait()
        url = f"https://koronavirus.gov.hu/elhunytak?page={page}" if page > 0 else "https://koronavirus.gov.hu/elhunytak"
        page_source = requests.get(url).content
        html = BeautifulSoup(page_source, "lxml")

        try:
            tbody_tag = find_only(html, "div", {"class": "view-content"}).table.tbody
            for tr_tag in tbody_tag.find_all("tr"):
                raw_row = {}
                for td_tag in tr_tag.find_all("td"):
                    raw_row[td_tag.attrs["class"][-1]] = td_tag.text.strip()
                raw_data.append(raw_row)

            page += 1
        except NoneExists:
            no_more_page = True


    with open('corona-hun-dead.csv', 'w') as f:  # You will need 'wb' mode in Python 2.x
        w = csv.DictWriter(f, raw_data[0].keys())
        w.writeheader()
        for row in raw_data:
            w.writerow(row)


