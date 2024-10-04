from bs4 import BeautifulSoup
import requests
import collections
import json

headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0',
}

case_study_map = collections.defaultdict(lambda: collections.defaultdict(list))

def scrape_search_result(key_for_request, value_for_request, key, value):
  with requests.Session() as s:
    r = s.post(
      'https://toolsofchange.com/en/case-studies/case-studies-search/advanced-search-results/',
      headers=headers,
      data={
        "do": "case_studies",
        "special": "mood",
        key_for_request: value_for_request,
      }
    )

    soup = BeautifulSoup(r.content, 'html.parser')

    for result in soup.find(class_="search_results_wrap").find_all('li'):
      link = result.find('a')
      if not link['href'].startswith('/en/case-studies/detail/'):
        print(link['href'] + "not a case study?")
        continue
      case_study_id = link['href'][len('/en/case-studies/detail/'):]
      case_study_map[case_study_id][key].append(value)

def scrape_topics():
  page = requests.get("https://toolsofchange.com/en/case-studies/case-studies-search/")
  soup = BeautifulSoup(page.content, "html.parser")
  for option in soup.find('select', id="child2").find_all("option"):
    if option["value"] == "": # the header
      continue
    scrape_search_result("topic", option["value"], "Topic", option.text)


def scrape_locations():
  page = requests.get("https://toolsofchange.com/en/case-studies/case-studies-search/")
  soup = BeautifulSoup(page.content, "html.parser")
  for option in soup.find_all('select', id="child2")[1].find_all("option"):
    if option["value"] == "": # the header
      continue
    scrape_search_result("menu2", option["value"], "Location", option.text)


def scrape_toc():
  page = requests.get("https://toolsofchange.com/en/case-studies/case-studies-search/")
  soup = BeautifulSoup(page.content, "html.parser")
  for option in soup.find_all('select')[2].find_all("option"):
    if option["value"] == "": # the header
      continue
    scrape_search_result("Menu3", option["value"], "Tool of Change involved", option.text)

scrape_topics()
scrape_locations()
scrape_toc()
# TELL_DAD: i didn't do date, and the website doesn't go more recent than 2010 anyways
scrape_search_result("Landmark_designation", "1", "Landmark designation?", "Yes")
scrape_search_result("Landmark_designation", "0", "Landmark designation?", "No")
scrape_search_result("widespread_use", "yes", "Available for widespread use?", "Yes")
scrape_search_result("widespread_use", "no", "Available for widespread use?", "No")


print(json.dumps(case_study_map))
