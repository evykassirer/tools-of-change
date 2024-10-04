import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import re

# TODO
# - support french
# - add planning guide
# - search:
#     - topic, location, tool, landmark -- can scrape
#     - keyword -- this might be harder, but still important, can search the page content

lang = "en"

def generate_page(f, url, page_text, path_to_root, soup_adjuster=None, remove_intro_cap=True):
  scrape_images(page_text)

  page_text = page_text.replace('href="http://www.toolsofchange.com/', f'href="{path_to_root}/')
  page_text = page_text.replace("/public/", f"{path_to_root}/public/")
  page_text = page_text.replace("/userfiles/", f"{path_to_root}/userfiles/")
  french_home_path = "/fr/accueil"
  english_home_path = "/en/home/"
  page_text = page_text.replace(french_home_path, f"{path_to_root}{french_home_path}")
  page_text = page_text.replace(english_home_path, f"{path_to_root}{english_home_path}")

  page_text = page_text.replace(f'href="/{lang}/', f'href="{path_to_root}/{lang}/')

  soup = BeautifulSoup(page_text,"html.parser")

  remove_classes = ["sponsor_box", "sidebar_body"]
  if (remove_intro_cap):
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
      if not item.find('a').contents[0] in ["Français", "English"]:
        item.decompose()
  else:
    print(f"no corner nav found!! for {url}")


  main_nav = soup.find('div', id="nav_container")
  if lang == "en":
    nav_exclusions = ["Planning Guide"]
  if lang == "fr":
    nav_exclusions = ["Planification"]
  if main_nav:
    for item in main_nav.find_all('li'):
      if item.find('a').contents[0] in nav_exclusions:
        item.decompose()
  else:
    print(f"no main nav found!! for {url}")

  if (soup_adjuster):
    soup_adjuster(soup)

  f.write(str(soup))


def generate_stylesheets():
  stylesheet_path = "public/stylesheets/"
  if not os.path.exists(stylesheet_path):
      os.makedirs(stylesheet_path)
  for sheet in ["default", "tables", "print", "thickbox", "sortmenu"]:
    page = requests.get(f"https://toolsofchange.com/public/stylesheets/{sheet}.css")
    scrape_images(page.text)
    text = page.text.replace("/public/", "../../public/")
    text = text.replace("ï»¿", "")
    with open(f"public/stylesheets/{sheet}.css", "x") as f:
      f.write(text)

downloaded_images = set()
def scrape_images(page_text):
  images = (
    re.findall(r'url\(\/public\/images\/(.+)\)', page_text) +
    re.findall(r'url\(\.\.\/images\/(.+)\)', page_text) +
    re.findall(r'src=\"\/public\/images\/(.+?)\"', page_text)
  )
  for img in images:
    if img not in downloaded_images:
      img_path = f"public/images/{img}"
      download_image(img_path)
      downloaded_images.add(img_path)

  for img in re.findall(r'src=\"\/userfiles\/Image\/(.+?)"', page_text):
    img_path = f"userfiles/Image/{img}"
    download_image(img_path)
    downloaded_images.add(img_path)

def download_image(image_path):
  imgURL = f"https://toolsofchange.com/{urllib.parse.quote(image_path)}"
  try:
    urllib.request.urlretrieve(imgURL, f"./{image_path}")
  except Exception as e:
    print(f"couldn't find {image_path}")
    print(e)


def generate_case_studies_homepage(page):
  if lang == "en":
    case_studies_home_url = "en/case-studies/"
  else:
    case_studies_home_url = "fr/etudes-de-cas/"
  if not os.path.exists(case_studies_home_url):
    os.makedirs(case_studies_home_url)
  with open(case_studies_home_url + "index.html", "x") as f:
    page_text = page.text
    page_text = page_text.replace(f"/{case_studies_home_url}", "./")
    generate_page(f, case_studies_home_url, page_text, "../..")

def generate_tools_of_change():
  if lang == "en":
    url = "en/tools-of-change/"
  else:
    url = "fr/outils-de-changement/"

  page = requests.get("https://toolsofchange.com/" + url)
  if not os.path.exists(url):
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
    if not os.path.exists(url):
        os.makedirs(url)
    with open(url + "index.html", "x") as f:
      def soup_adjuster(soup):
        # Remove right column that's only relevant when logged in
        for tag in soup.findAll(attrs={'class':'plan_col_right'}):
            tag['style'] = "display: none;"
        for tag in soup.findAll(attrs={'class':'left_content_2col'}):
            tag['style'] = "background: #e5edee;"
        for tag in soup.findAll(attrs={'class':'plan_col_left'}):
            tag['style'] = "width: 90%;"
        # Remove "login to save plans" thing (top and bottom of page)
        for bar in soup.find_all('div', class_="bar"):
          bar.decompose()

      generate_page(f, url, page.text, "../../..", soup_adjuster)


def generate_topic_resources():
  # (only relevant for english)
  download_image("/userfiles/Web-based social marketing resources-2023-V2.pdf")

  if lang == "en":
    url = "en/topic-resources/"
  else:
    url = "fr/ressources-de-sujets/"
  page = requests.get("https://toolsofchange.com/" + url)
  if not os.path.exists(url):
      os.makedirs(url)
  with open(url + "index.html", "x") as f:
    generate_page(f, url, page.text, "../..")


  resource_soup = BeautifulSoup(page.content, "html.parser")
  resource_links = resource_soup.find('div', class_="topic_resources_detail").find_all('a')
  for section in resource_soup.find_all('div', class_="topic_resources_detail_pad"):
    resource_links = resource_links + section.find_all('a')

  for resource in resource_links:
    url = resource['href']
    if url[0] == "/":
      url = url[1:]
    if url.startswith("http://www.toolsofchange.com/"):
      url = url[len("http://www.toolsofchange.com/"):]
    if url[-1] != "/":
      url += "/"

    page = requests.get("https://toolsofchange.com/" + url)
    if not os.path.exists(url):
        os.makedirs(url)
    with open(url + "index.html", "x") as f:
      # maybe remove the two advanced search boxes?
      generate_page(f, url, page.text, "../../..")


def generate_case_study_pages(page):
  soup = BeautifulSoup(page.content, "html.parser")

  headers = soup.find_all(class_="sub_header_2col")

  urls = [
    header.find("a", href=True)['href']
    for header in headers
  ]

  for url in urls:
    if url[0] == "/":
      url = url[1:]
    if not os.path.exists(url):
        os.makedirs(url)
    with open(url + "index.html", "x") as f:
      page = requests.get("https://toolsofchange.com/" + url)
      generate_page(f, url, page.text, "../../../..")


def generate_simple_pages():
  if lang == "en":
    urls = [
      "en/contact-us/",
      "en/workshops/",
      "en/workshops/face-to-face/",
      "en/about-us/",
      "en/landmark/",
      "en/help/", # TODO: remove thing about creating an account
      "en/terms/",
    ]
  else:
    urls = [
      "fr/contactez-nous/",
      "fr/ateliers/",
      "fr/ateliers/présentations-personnalisé-par-webinaire/",
      "fr/au-sujet-de-nous/", # TODO: tell dad this isn't translated
      # Seems like landmark just isn't a thing in french..?
      "fr/aide/",
      "fr/modalités-d'utilisation/",
    ]

  for url in urls:
    page = requests.get("https://toolsofchange.com/" + url)
    if not os.path.exists(url):
        os.makedirs(url)
    with open(url + "index.html", "x") as f:
      generate_page(f, url, page.text, "../..")

def generate_homepage():
  if lang == "en":
    url = "en/home/"
  else:
    url = "fr/accueil/"

  page = requests.get("https://toolsofchange.com/" + url)

  if not os.path.exists(url):
      os.makedirs(url)
  with open(url + "index.html", "x") as f:
    def soup_adjuster(soup):
      # Remove "Planning Guide" focus box for now (it's the first one)
      soup.find('div', class_="focus_box").decompose()
      # TODO: Ask dad about if the news section is important,
      # since it seems nontrivial to add.
      soup.find('div', class_="latest_news_area").decompose()
      # Remove left margin now that the news is gone
      soup.find(attrs={'class':'webinar_area_wrap'})['style'] = "margin: 0;"
      for link in soup.find_all('a'):
        if "https://clicky.com" in link['href']:
          link.decompose()
    generate_page(f, url, page.text, "../..", soup_adjuster, False)

  homepage_soup = BeautifulSoup(page.content, "html.parser")
  for intro_link in homepage_soup.find('div', class_="intro_box").find_all('a'):
    url = intro_link['href']
    if url[0] == "/":
      url = url[1:]
    page = requests.get("https://toolsofchange.com/" + url)
    if not os.path.exists(url):
        os.makedirs(url)
    with open(url + "index.html", "x") as f:
      generate_page(f, url, page.text, "../../..")


# os.makedirs("./public/images/")
# os.makedirs("./userfiles/Image")
# generate_stylesheets()

# generate_homepage()
# generate_simple_pages()
# generate_topic_resources()
# generate_tools_of_change()
# case_studies_homepage = requests.get("https://toolsofchange.com/en/case-studies/?max=1000")
# generate_case_studies_homepage(case_studies_homepage)
# generate_case_study_pages(case_studies_homepage)

lang = "fr"
generate_homepage()
generate_simple_pages()
generate_topic_resources()
generate_tools_of_change()
case_studies_homepage = requests.get("https://toolsofchange.com/fr/etudes-de-cas/?max=1000")
generate_case_studies_homepage(case_studies_homepage)
generate_case_study_pages(case_studies_homepage)
