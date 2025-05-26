import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import re
import json
import unicodedata


# TODO:
# - figure out search again and document it and see if dad's okay with how it works
# - add topic resources to metadata for search
# - once search is finalized, integrate it into the UI

"""
notes for dad:
* some case studies are missing from search results (more for french, most recent for english)
* some images aren't there
* fr/au-sujet-de-nous/ isn't translated
* landmark doesn't seem to be a part of the french site
* french tool name inconsistencies
  * Réaction tool isn't called that, it's called rétroaction
  * Motivation is called motivateurs
  * Soutenir la motivation à long terme --> Soutenir la motivation au fil du temps
"""

# TODO for when this is converted to main site, things to change manually:
#
# - add a hardcoded latest news box and news page
# - remove thing about creating an account on the help pages (en/fr)

with open('case_study_data.json', 'r') as file:
    case_study_data = json.load(file)

with open('case_study_data_fr.json', 'r') as file:
    case_study_data_fr = json.load(file)

lang = "en"

# Links to tools exist with and without accents, so we normalize to have links
# never have accents (which is the standard for urls)
# Doing it this way feels easier and more efficient to check than normalizing
# every url (which might even break other things, e.g. "modalités-d'utilisation"
# has an accent) but probably I should at some point normalize everything more
# consistently including creating urls?? Because idk if other things are still
# broken in this way.
french_tools_with_accents = [
  "communications-personnalisées-percutantes",
  "mesures-financières-incitatives-et-dissuasives",
  "rétroaction",
  "surmonter-des-obstacles-spécifiques",
  "de-bouche-à-oreille",
  "médias",
  "visites-à-domicile",
]

def remove_accents(s):
  return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8', 'ignore')

french_url_replacements = [
  [f"outils-de-changement/{tool}", f"outils-de-changement/{remove_accents(tool)}"]
  for tool in french_tools_with_accents
]

def generate_page(f, url, page_text, path_to_root, soup_adjuster=None):
  scrape_images(page_text)
  scrape_userfiles(page_text)

  url_replacements = [
    ['http://toolsofchange.com', f'{path_to_root}'],
    ['http://www.toolsofchange.com', f'{path_to_root}'],
    ['https://www.toolsofchange.com', f'{path_to_root}'],
    ['https://toolsofchange.com', f'{path_to_root}'],
    ['www.toolsofchange.com', f'{path_to_root}'],
    ["'/public/", f"'{path_to_root}/public/"],
    ['"/public/', f'"{path_to_root}/public/'],
    ['(/public/', f'({path_to_root}/public/'],
    ["'/userfiles/", f"'{path_to_root}/userfiles/"],
    ['"/userfiles/', f'"{path_to_root}/userfiles/'],
    ['(/userfiles/', f'({path_to_root}/userfiles/'],
  ]

  if lang == "fr":
    url_replacements = url_replacements + french_url_replacements

  # TODO -- this should probably be more careful to only replace text in href/src tags
  for before, after in url_replacements:
    page_text = page_text.replace(before, after)

  french_home_path = "/fr/accueil"
  english_home_path = "/en/home/"
  page_text = page_text.replace(french_home_path, f"{path_to_root}{french_home_path}")
  page_text = page_text.replace(english_home_path, f"{path_to_root}{english_home_path}")

  page_text = page_text.replace(f'href="/en/', f'href="{path_to_root}/en/')
  page_text = page_text.replace(f'href="/fr/', f'href="{path_to_root}/fr/')

  soup = BeautifulSoup(page_text,"html.parser")

  # forms get in the way of search working, and aren't needed since we got rid of accounts
  while True:
    form = soup.find("form")
    if not form:
      break
    form.unwrap()

  # metadata for search
  content_wrapper = soup.find(id="content_wrap")
  if not content_wrapper:
    print(url + " has no content wrap")
  else:
    if content_wrapper.find('div', class_="left_wrap"):
      content_wrapper.find('div', class_="left_wrap")["data-pagefind-body"] = None
    else:
      print(url + " has no left wrap in the content wrapper")

    if content_wrapper.find('h1'):
      content_wrapper.find('h1')["data-pagefind-meta"] = "title"
    elif content_wrapper.find('h2'):
      content_wrapper.find('h2')["data-pagefind-meta"] = "title"
      if "/topic-resources/detail" not in url and '/ressources-de-sujets/detail' not in url:
        print(url + " had an h2, but go check")
    else:
      print(url + " has no headers in content wrapper?")


  image_tag = soup.new_tag("img")
  image_tag['style'] = "display: none;"
  image_tag['src'] = f"{path_to_root}/public/images/leaf_icon.gif"
  image_tag["data-pagefind-meta"] = "image[src]"
  soup.find("body").append(image_tag)

  remove_classes = ["sponsor_box", "sidebar_body"]
  if not soup.find("div", class_="intro_box"):
    remove_classes += ["intro_cap_top", "intro_cap_bottom"]
  for remove_class in remove_classes:
    div = soup.find('div', class_=remove_class)
    if div:
      div.decompose()
    else:
      print(f"couldn't find .{remove_class} to remove for {url}")

  footer_right = soup.find('div', class_="footer_right")
  if lang == "en":
    footer_exclusions = ["Search", "My Account"]
  if lang == "fr":
    footer_exclusions = ["Recherche", "Mon dossier"]
  if footer_right:
    for item in footer_right.find_all('li'):
      if item.find('a').contents[0] in footer_exclusions:
        item.decompose()
  else:
    print(f"no footer found!! for {url}")

  corner_nav = soup.find('ul', id="quicknav")
  if corner_nav:
    for item in corner_nav.find_all('li'):
      # [done] TELL_DAD: what the language change links to is really random
      # e.g. https://toolsofchange.com/fr/etudes-de-cas/recherche-de-etudes-de-cas/
      if not item.find('a').contents[0] in ["Français", "English"]:
        item.decompose()
  else:
    print(f"no corner nav found!! for {url}")

  if (soup_adjuster):
    soup_adjuster(soup)

  f.write(str(soup))


def generate_stylesheets():
  stylesheet_path = "public/stylesheets/"
  os.makedirs(stylesheet_path)
  for sheet in ["default", "tables", "print", "thickbox", "sortmenu"]:
    page = requests.get(f"https://toolsofchange.com/public/stylesheets/{sheet}.css")
    scrape_images(page.text)
    scrape_userfiles(page.text)
    text = page.text.replace("/public/", "../../public/")
    text = text.replace("ï»¿", "")
    with open(f"public/stylesheets/{sheet}.css", "x") as f:
      f.write(text)

downloaded_images = set()
downloaded_files = set()
def scrape_images(page_text):
  images = (
    re.findall(r'url\(\/public\/images\/(.+)\)', page_text) +
    re.findall(r'url\(\.\.\/images\/(.+)\)', page_text) +
    re.findall(r'src=\"\/public\/images\/(.+?)\"', page_text)
  )
  for img in images:
    if img not in downloaded_images:
      img_path = f"public/images/{img}"
      download_file(img_path)
      downloaded_images.add(img_path)

def scrape_userfiles(page_text):
  for file_name in re.findall(r'\/userfiles\/(.+?)"', page_text):
    file_path = f"userfiles/{file_name}"
    download_file(file_path)
    downloaded_files.add(file_path)

def download_file(file_path):
  file_url = f"https://toolsofchange.com/{urllib.parse.quote(file_path)}"
  try:
    urllib.request.urlretrieve(file_url, f"./{file_path}")
  except Exception as e:
    print(f"couldn't find {file_path}")
    print(e)


def generate_case_studies_homepage(page):
  if lang == "en":
    case_studies_home_url = "en/case-studies/"
  else:
    case_studies_home_url = "fr/etudes-de-cas/"
  os.makedirs(case_studies_home_url)
  with open(case_studies_home_url + "index.html", "x") as f:
    page_text = page.text
    page_text = page_text.replace(f"/{case_studies_home_url}", "./")
    def soup_adjuster(soup):
      # This is the "sort by latest, last 5 10 15" etc bar
      soup.find('div', class_="bar").decompose()
    generate_page(f, case_studies_home_url, page_text, "../..", soup_adjuster)

def generate_planning_guide():
  if lang == "en":
    url = "en/planning-guide/"
  else:
    url = "fr/guide-de-planification/"

  page = requests.get("https://toolsofchange.com/" + url)
  os.makedirs(url)
  with open(url + "index.html", "x") as f:
    def soup_adjuster(soup):
      # "Login to save plans"
      if lang == "en":
        soup.find('div', class_="bar_tall").decompose()
      else:
        soup.find('div', class_="bar").decompose()
      # now that that's gone, we should add a bit more padding here
      soup.find('div', id="steps_nav")['style'] = "margin-top: 20px;"
    generate_page(f, url, page.text, "../..", soup_adjuster)

  guide_soup = BeautifulSoup(page.content, "html.parser")
  steps = guide_soup.find('div', id="steps_nav").find_all('a')
  for step in steps:
    url = cleanup_url(step['href'])
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      def soup_adjuster(soup):
        # Remove "login to save plans" thing (top and bottom of page)
        for bar in soup.find_all('div', class_="bar"):
          bar.decompose()
        # This is where the user input would go if there were accounts
        for your_program_box in soup.find_all(class_="thickbox"):
          if your_program_box.find_previous("tr"):
            your_program_box.find_previous("tr").decompose();
          else:
            your_program_box.decompose()

      generate_page(f, url, page.text, "../../..", soup_adjuster)

def generate_tools_of_change():
  if lang == "en":
    url = "en/tools-of-change/"
  else:
    url = "fr/outils-de-changement/"

  page = requests.get("https://toolsofchange.com/" + url)
  os.makedirs(url)
  with open(url + "index.html", "x") as f:
    generate_page(f, url, page.text, "../..")

  tools_soup = BeautifulSoup(page.content, "html.parser")
  tool_links = tools_soup.find('div', class_="left_content").find_all('a')
  for tool in tool_links:
    url = tool['href']
    if url[0] == "/":
      url = url[1:]
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      def soup_adjuster(soup):
        # Remove "login to save plans" thing (top and bottom of page)
        for bar in soup.find_all('div', class_="bar"):
          bar.decompose()
        # This is where the user input would go if there were accounts
        for your_program_box in soup.find_all(class_="thickbox"):
          if your_program_box.find_previous("tr"):
            your_program_box.find_previous("tr").decompose();
          else:
            your_program_box.decompose()

      generate_page(f, url, page.text, "../../..", soup_adjuster)


def cleanup_url(url):
  if url[0] == "/":
    url = url[1:]
  if url.startswith("http://www.toolsofchange.com/"):
    url = url[len("http://www.toolsofchange.com/"):]
  if url[-1] != "/":
    url += "/"
  return url

def generate_topic_resources():

  if lang == "en":
    topic_resource_url = "en/topic-resources/"
  else:
    topic_resource_url = "fr/ressources-de-sujets/"

  # Generate homepage
  page = requests.get("https://toolsofchange.com/" + topic_resource_url)
  os.makedirs(topic_resource_url)
  with open(topic_resource_url + "index.html", "x") as f:
    generate_page(f, topic_resource_url, page.text, "../..")

  # Generate pages for each of the topics
  homepage_soup = BeautifulSoup(page.content, "html.parser")
  resource_page_links = homepage_soup.find('div', class_="topic_resources_detail").find_all('a')
  for section in homepage_soup.find_all('div', class_="topic_resources_detail_pad"):
    resource_page_links = resource_page_links + section.find_all('a')

  for resource_page in resource_page_links:
    url = cleanup_url(resource_page['href'])
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      # TODO: maybe remove the two advanced search boxes?
      generate_page(f, url, page.text, "../../..")

    # Now generate the pages for each resource
    soup = BeautifulSoup(page.content, "html.parser")

    for link in soup.find_all('a'):
      if topic_resource_url + "detail" in link['href']:
        url = cleanup_url(link['href'])
        if os.path.exists(url):
          continue
        os.makedirs(url)
        page = requests.get("https://toolsofchange.com/" + url)
        with open(url + "index.html", "x") as f:
          generate_page(f, url, page.text, "../../../..")


def generate_case_study_pages(page):
  soup = BeautifulSoup(page.content, "html.parser")

  headers = soup.find_all(class_="sub_header_2col")

  urls = [
    header.find("a", href=True)['href']
    for header in headers
  ]

  for url in urls:
    url = cleanup_url(url)
    os.makedirs(url)
    if lang == "en":
      case_study_id = url[len('en/case-studies/detail/'):-1]
      if case_study_id not in case_study_data_fr:
        print("can't find id in search results (en) " + case_study_id)
        metadata = {}
      else:
        metadata = case_study_data[case_study_id]
    else:
      case_study_id = url[len('fr/etudes-de-cas/detail/'):-1]
      if case_study_id not in case_study_data_fr:
        print("can't find id in search results (fr) " + case_study_id)
        metadata = {}
      else:
        metadata = case_study_data_fr[case_study_id]

    def soup_adjuster(soup):
      for key, value_list in metadata.items():
        for value in value_list:
          new_tag = soup.new_tag("span")
          new_tag['style'] = "display: none;"
          new_tag['data-pagefind-filter'] = f"{key}: {value}"
          soup.find("body").append(new_tag)
    page = requests.get("https://toolsofchange.com/" + url)
    with open(url + "index.html", "x") as f:
      generate_page(f, url, page.text, "../../../..", soup_adjuster)


def generate_simple_pages():
  if lang == "en":
    urls = [
      "en/contact-us/",
      "en/workshops/",
      "en/workshops/face-to-face/",
      "en/about-us/",
      "en/about-us/workbook-acknowledgements/"
      "en/landmark/",
      "en/help/", # TODO: remove thing about creating an account
      "en/terms/",
    ]
  else:
    urls = [
      "fr/contactez-nous/",
      "fr/ateliers/",
      "fr/ateliers/présentations-personnalisé-par-webinaire/",
      "fr/au-sujet-de-nous/",
      "fr/au-sujet-de-nous/cahier-de-travail-/"
      "fr/aide/",
      "fr/modalités-d'utilisation/",
    ]

  for url in urls:
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      # TODO(cleanup): i can just calculate this in the generate_page function, which would be better
      path_to_root = "../.." if url.count("/") == 2 else "../../.."
      generate_page(f, url, page.text, path_to_root)

def generate_homepage():
  if lang == "en":
    url = "en/home/"
  else:
    url = "fr/accueil/"

  page = requests.get("https://toolsofchange.com/" + url)

  os.makedirs(url)
  with open(url + "index.html", "x") as f:
    def soup_adjuster(soup):
      # TODO: put a hardcoded news section here
      soup.find('div', class_="latest_news_area").decompose()
      # Remove left margin now that the news is gone
      soup.find(attrs={'class':'webinar_area_wrap'})['style'] = "margin: 0;"
      for link in soup.find_all('a'):
        if "https://clicky.com" in link['href']:
          link.decompose()
    generate_page(f, url, page.text, "../..", soup_adjuster)

  homepage_soup = BeautifulSoup(page.content, "html.parser")
  for intro_link in homepage_soup.find('div', class_="intro_box").find_all('a'):
    url = cleanup_url(intro_link['href'])
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      generate_page(f, url, page.text, "../../..")


def setup():
  print("setup")
  os.makedirs("./public/images/")
  os.makedirs("./userfiles/Image")
  generate_stylesheets()

def generate_english_site():
  global lang
  lang = "en"
  print("english")
  print("homepage")
  generate_homepage()
  print("simple pages")
  generate_simple_pages()
  print("topic resources")
  generate_topic_resources()
  print("tools of change")
  generate_tools_of_change()
  print("case studies")
  case_studies_homepage = requests.get("https://toolsofchange.com/en/case-studies/?max=1000")
  generate_case_studies_homepage(case_studies_homepage)
  generate_case_study_pages(case_studies_homepage)
  print("planning guide")
  generate_planning_guide()

def generate_french_site():
  global lang
  lang = "fr"
  print("french")
  print("homepage")
  generate_homepage()
  print("simple pages")
  generate_simple_pages()
  print("topic resource")
  generate_topic_resources()
  print("tools of change")
  generate_tools_of_change()
  print("case studies")
  case_studies_homepage = requests.get("https://toolsofchange.com/fr/etudes-de-cas/?max=1000")
  generate_case_studies_homepage(case_studies_homepage)
  generate_case_study_pages(case_studies_homepage)
  print("planning guide")
  generate_planning_guide()

setup()
generate_english_site()
generate_french_site()
