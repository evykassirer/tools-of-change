from bs4 import BeautifulSoup
import requests
import collections
import json

headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0',
}

results_map = collections.defaultdict(lambda: collections.defaultdict(list))
lang = "en"

def scrape_case_study_search_result(key_for_request, value_for_request, key, value):
  if lang == "fr":
    url = "https://toolsofchange.com/fr/etudes-de-cas/recherche-de-etudes-de-cas/advanced-search-results/"
  elif lang == "en":
    url = 'https://toolsofchange.com/en/case-studies/case-studies-search/advanced-search-results/'

  with requests.Session() as s:
    r = s.post(
      url,
      headers=headers,
      data={
        "do": "case_studies",
        "special": "mood",
        key_for_request: value_for_request,
      }
    )

    soup = BeautifulSoup(r.content, 'html.parser')

    if lang == "en":
      case_study_url_part = '/en/case-studies/detail/'
    elif lang == "fr":
      case_study_url_part = '/fr/etudes-de-cas/detail/'

    for result in soup.find(class_="search_results_wrap").find_all('li'):
      link = result.find('a')
      if not link['href'].startswith(case_study_url_part):
        print(link['href'] + "not a case study?")
        continue
      case_study_id = link['href'][len(case_study_url_part):]
      results_map[case_study_id][key].append(value)

def scrape_topics(url, result_scraper):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")
  for option in soup.find('select', id="child2").find_all("option"):
    if option["value"] == "": # the header
      continue
    user_facing_key = "Topic" if lang == "en" else "Sujet"
    result_scraper("topic", option["value"], user_facing_key, option.text)


def scrape_locations(url, result_scraper):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")
  for option in soup.find_all('select', id="child2")[1].find_all("option"):
    if option["value"] == "": # the header
      continue
    user_facing_key = "Location" if lang == "en" else "Endroit"
    result_scraper("menu2", option["value"], user_facing_key, option.text)


def scrape_toc(url, result_scraper):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")
  for option in soup.find_all('select')[2].find_all("option"):
    if option["value"] == "": # the header
      continue
    user_facing_key = "Tool of Change involved" if lang == "en" else "Outils de changement utilisés"
    result_scraper("Menu3", option["value"], user_facing_key, option.text)

def scrape_en_case_studies():
  results_map.clear()
  global lang
  lang = "en"
  url = 'https://toolsofchange.com/en/case-studies/case-studies-search/'

  scrape_topics(url, scrape_case_study_search_result)
  scrape_locations(url, scrape_case_study_search_result)
  scrape_toc(url, scrape_case_study_search_result)
  scrape_case_study_search_result("Landmark_designation", "1", "Landmark designation?", "Yes")
  scrape_case_study_search_result("Landmark_designation", "0", "Landmark designation?", "No")
  scrape_case_study_search_result("widespread_use", "yes", "Available for widespread use?", "Yes")
  scrape_case_study_search_result("widespread_use", "no", "Available for widespread use?", "No")


  with open("case_study_data.json", "x") as f:
    f.write(json.dumps(results_map))

def scrape_fr_case_studies():
  results_map.clear()
  global lang
  lang = "fr"
  url = "https://toolsofchange.com/fr/etudes-de-cas/recherche-de-etudes-de-cas/"

  scrape_topics(url, scrape_case_study_search_result)
  scrape_locations(url, scrape_case_study_search_result)
  scrape_toc(url, scrape_case_study_search_result)
  scrape_case_study_search_result("Landmark_designation", "1", "Landmark designation?", "Oui")
  scrape_case_study_search_result("Landmark_designation", "0", "Landmark designation?", "Non")
  scrape_case_study_search_result("widespread_use", "yes", "Afficher seulement les études de cas des programmes qui font l'objet d'une diffusion générale", "Oui")
  scrape_case_study_search_result("widespread_use", "no", "Afficher seulement les études de cas des programmes qui font l'objet d'une diffusion générale", "Non")

  # print(json.dumps(results_map))
  with open("case_study_data_fr.json", "x") as f:
    f.write(json.dumps(results_map))


def scrape_topic_resource_search_result(key_for_request, value_for_request, key, value):
  if lang == "fr":
    url = "https://toolsofchange.com/fr/ressources-de-sujets/recherche-de-ressources-de-sujets/advanced-search-results/"
  elif lang == "en":
    url = 'https://toolsofchange.com/en/topic-resources/topic-resources-search/advanced-search-results/'

  with requests.Session() as s:
    r = s.post(
      url,
      headers=headers,
      data={
        "do": "topic_resources",
        "special": "mood",
        key_for_request: value_for_request,
      }
    )

    soup = BeautifulSoup(r.content, 'html.parser')

    if lang == "en":
      topic_resource_url_part = '/en/topic-resources/detail/'
    elif lang == "fr":
      topic_resource_url_part = '/fr/ressources-de-sujets/detail/'

    for result in soup.find(class_="search_results_wrap").find_all('li'):
      link = result.find('a')
      if not link['href'].startswith(topic_resource_url_part):
        print(link['href'] + "not a case study?")
        continue
      resource_id = link['href'][len(topic_resource_url_part):]
      results_map[resource_id][key].append(value)


def scrape_en_topic_resources():
  results_map.clear()
  global lang
  lang = "en"
  url = "https://toolsofchange.com/en/topic-resources/topic-resources-search/"

  scrape_topics(url, scrape_topic_resource_search_result)
  scrape_locations(url, scrape_topic_resource_search_result)

  # TODO Topic Resources by Category

  with open("topic_resource_data.json", "x") as f:
    f.write(json.dumps(results_map))

scrape_en_case_studies()
scrape_fr_case_studies()

# TODO: topic resource scrape

# TODO: tell dad french results for topic resources are broken, links don't work (missing id)
