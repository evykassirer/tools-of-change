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

# TODO(post-backup) for when this is converted to main site, things to change manually:
#
# - add a redirect from toolsofchange.com to en/home/
# - manually fix /"en/case-studies/detail/138" to remove the quotes
# - manually replace <a ""="" 127""""="" .... with '<a href="/fr/etudes-de-cas/detail/127/'
# - manually remove the 3 remaining "Login to Save Plans for Tools of Change" that are there for some reason
# - add a hardcoded latest news box and news page
# - remove thing about creating an account on the help pages (en/fr)
#    - any user/create link
# - remove search stuff noted in check_complete_backup
# - there's a Français (top corner) link to /fr/aide/landmark(f)  which has nothing and also doesn't make sense, change it
#   - and another for fr/aide/landmark-badge

with open('case_study_data.json', 'r') as file:
    case_study_data = json.load(file)

with open('case_study_data_fr.json', 'r') as file:
    case_study_data_fr = json.load(file)

lang = "en"

french_home_path = "/fr/accueil"
english_home_path = "/en/home/"

# Files that aren't on the site we're scraping from, so don't worry about them
# when fetches give errors.
known_missing_files = [
  'public/images/transparent.gif', # this one doesn't matter
  'public/images/toc_landmark_badge_170x250.jpg', # doesn't matter (not displayed anywhere)
  'userfiles/Image/Street.jpg',
  'userfiles/File/Handout_TOC_Highlights_2012_03_01_2pp.pdf',
  'userfiles/CrugerK_TOC_TC_EN_2010_02_23_2pp.pdf',
  'userfiles/CrugerK_TOC_TC_EN_2010_02_23_6pp.pdf',
  'userfiles/Smart Commute Q4 Report print.pdf',
  'userfiles/Handouts%20-%20May%209%20-2013.pdf',
  'userfiles/Smarter Travel Case Handout2.pdf',
  'images/documentimages/jeep/jeep-1.jpg',
  'images/documentimages/jeep/Jeep-2.jpg',
  'images/documentimages/bc21/bc21-1.jpg',
  'images/documentimages/tools/peersg-1.jpg',
  'images/documentimages/tools/feedback-1.jpg',
  'images/documentimages/roadcrew/roadcrew_logo.jpg',
  'images/documentimages/roadcrew/roadcrew_underwear.jpg',
  'images/documentimages/watersmart/WaterSmart-2.jpg',
  'images/documentimages/watersmart/WaterSmart-1.jpg',
  'images/documentimages/recap/Recap-1.jpg',
  'images/documentimages/whitney/Whitney-1.jpg',
  'images/documentimages/Earthworks/EarthWorks-3.jpg',
  'images/documentimages/Earthworks/EarthWorks-1.jpg',
  'images/documentimages/Quinte/Quinte-1.jpg',
]

# Erroneously encoded urls, that we want to change back so we can properly
# fetch them
encoded_urls = [
  ['userfiles/Image//Burlington%20map%203.PNG', 'userfiles/Image/Burlington map 3.PNG'],
  ['userfiles/Image//Chatham%20Area%20Map.JPG', 'userfiles/Image/Chatham Area Map.JPG'],
  ['userfiles/Image//Andrew%20Bio%20Picture.jpg', 'userfiles/Image/Andrew Bio Picture.jpg'],
  ['userfiles/Virgin Atlantic&#8217;s Airline Captains Improve Fuel Efficiency -2021-12-16(1).pdf', 'userfiles/Virgin Atlantic’s Airline Captains Improve Fuel Efficiency -2021-12-16(1).pdf'],
  ['userfiles/Image/Star%20Party.png', 'userfiles/Image/Star Party.png'],
  ['userfiles/File//ClimateSmart%20Case%20Study%20FINAL2.pdf', 'userfiles/File/ClimateSmart Case Study FINAL2.pdf'],
  ['userfiles/File//UGA%20Recycling%20Bin%20Feedback.pdf', 'userfiles/File/UGA Recycling Bin Feedback.pdf'],
  ['userfiles/Q&amp;A.pdf', 'userfiles/Q&A.pdf'],
  ['"/images/documentimages/AQPortland/prizedraw"', '"/images/documentimages/AQPortland/prizedraw.gif"'],
  ['landmark-case-studies-%28transportation%29/', 'landmark-case-studies-(transportation)/'],
  ["s%C3%A9curit%C3%A9-routi%C3%A8re", "securite-routiere"],
  ["m%C3%A9decine-du-travail", "medecine-du-travail"],
  ["efficacit%C3%A9-%C3%A9nerg%C3%A9tique", "efficacite-energetique"],
]

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

french_url_replacements.append(["études-de-cas", "etudes-de-cas"])
french_url_replacements.append([
  "ressources-de-sujets/santé-cardiovasculaire",
  "ressources-de-sujets/sante-cardiovasculaire"
])
french_url_replacements.append([
  "guide-de-planification/obtenir-informé/",
  "guide-de-planification/obtenir-informe/"
])

def generate_page(f, url, page_text, soup_adjuster=None):
  url = cleanup_url(url)
  path_to_root = "/".join([".." for n in range(url.count("/"))])

  for before, after in encoded_urls:
    page_text = page_text.replace(before, after)

  scrape_images(page_text)
  scrape_userfiles(page_text)

  for before, after in [
    ['(/public/', f'({path_to_root}/public/'],
    ['(/userfiles/', f'({path_to_root}/userfiles/'],
    # these don't get caught in the replacements below because they're in comments of JS
    ['<td class="go_area"><input src="/public', f'<td class="go_area"><input src="{path_to_root}/public'],
    ['<img src="http://www.toolsofchange.com/public/images/toc_landmark_badge_170x250.jpg', f'<img src="{path_to_root}/public/images/toc_landmark_badge_170x250.jpg'],
    ['$("a.expose3").html(\'<img src="/public/images', f'$("a.expose3").html(\'<img src="{path_to_root}/public/images'],

  ]:
    page_text = page_text.replace(before, after)


  url_replacements = [
    # Broken on TOC but I fixed them here
    ["fr/etudes-de-cas/detail/127", "fr/etudes-de-cas/detail/445"],
    ["utils-de-changement/programmes-en-milieu-de-travail-qui-affectent-le-foyer/Programs",
     "utils-de-changement/programmes-en-milieu-de-travail-qui-affectent-le-foyer"],
    ["case-studies/detail/635//", "case-studies/detail/635/"],
    ["/&quot;English/CaseStudies/default.asp?ID=138&quot;", 'en/case-studies/detail/138/'],
    ["tools-of-change.com", "toolsofchange.com"],
    ["toc/fr/etudes-de-cas/detail/10", "fr/etudes-de-cas/detail/10"],
    ["http:///en/", "/en/"],
    ["http://en/", "/en/"],
    ["http://  /en/", "/en/"],

    # old urls
    ["francais/ToolsofChange/default.asp?Section=motivation", "fr/outils-de-changement/soutenir-la-motivation-au-fil-du-temps/"],
    ["francais/ToolsofChange/default.asp?Section=Motivation", "fr/outils-de-changement/soutenir-la-motivation-au-fil-du-temps/"],
    ["Francais/ToolsofChange/default.asp?Section=Motivation", "fr/outils-de-changement/soutenir-la-motivation-au-fil-du-temps/"],
    ["francais/ToolsofChange/default.asp?Section=commitment", "fr/outils-de-changement/obtenir-un-engagement/"],
    ["francais/ToolsofChange/default.asp?Section=Commitment", "fr/outils-de-changement/obtenir-un-engagement/"],
    ["francais/ToolsofChange/default.asp?Section=Norm", "fr/outils-de-changement/attrait-des-normes/"],
    ["Francais/ToolsofChange/default.asp?Section=Norm", "fr/outils-de-changement/attrait-des-normes/"],
    ["francais/ToolsofChange/default.asp?Section=Financial", "fr/outils-de-changement/Mesures-financieres-incitatives-et-dissuasives/"],
    ["Francais/ToolsofChange/default.asp?Section=Financial", "fr/outils-de-changement/Mesures-financieres-incitatives-et-dissuasives/"],
    ["francais/ToolsofChange/default.asp?Section=Communication", "fr/outils-de-changement/communications-personnalisees-percutantes/"],
    ["francais/ToolsofChange/default.asp?Section=Barriers", "fr/outils-de-changement/surmonter-des-obstacles-specifiques/"],
    ["Francais/ToolsofChange/default.asp?Section=Barriers", "fr/outils-de-changement/surmonter-des-obstacles-specifiques/"],
    ["Francais/ToolsofChange/default.asp?Section=Media", "fr/outils-de-changement/medias/"],
    ["Francais/ToolsofChange/default.asp?Section=Home", "fr/outils-de-changement/Visites-a-domicile/"],
    ["Francais/ToolsofChange/default.asp?Section=Word", "fr/outils-de-changement/de-bouche-a-oreille/"],
    ["English/ToolsofChange/default.asp?Section=WorkPrograms", "en/tools-of-change/work-programs/"],
    ["English/ToolsofChange/default.asp?Section=Work", "en/tools-of-change/work-programs/"],
    ["English/PlanningGuide/default.asp?Section=Partners", "en/planning-guide/developing-partners/"],
    ["English/firstsplit.asp", "en/home"],
    ["English/CaseStudies/default.asp?ID=", "en/case-studies/detail/"],
    ["Francais/CaseStudies/default.asp?ID=", "fr/etudes-de-cas/detail/"],
    ["francais/CaseStudies/default.asp?ID=", "fr/etudes-de-cas/detail/"],

    ["fr/outils-de-changement/animateurs-de-quartier / leaderspopulaires",
     "fr/outils-de-changement/animateurs-de-quartier---meneurs-populaires"],
    ["fr/outils-de-changement/animateurs-de-quartier/-meneurs-populaires",
     "fr/outils-de-changement/animateurs-de-quartier---meneurs-populaires"],
    ["fr/ressources-de-sujets/Santé cardiovasculaire", "fr/ressources-de-sujets/sante-cardiovasculaire"],
    ['http://toolsofchange.com', f'{path_to_root}'],
    ['http://www.toolsofchange.com', f'{path_to_root}'],
    ['https://www.toolsofchange.com', f'{path_to_root}'],
    ['https://toolsofchange.com', f'{path_to_root}'],
    ['www.toolsofchange.com', f'{path_to_root}'],
  ]

  url_replacements = url_replacements + french_url_replacements

  def make_url_replacements(link, attr):
    link[attr] = link[attr].strip()
    for before, after in url_replacements:
      link[attr] = link[attr].replace(before, after)
    for prefix in ['en', 'fr']:
      if link[attr].startswith(prefix):
        link[attr] = "/" + link[attr]
    for prefix in ['/en', '/fr', '/public', '/userfiles']:
      if link[attr].startswith(prefix):
        link[attr] = path_to_root + link[attr]


  soup = BeautifulSoup(page_text,"html.parser")
  for link in soup.find_all('a'):
    if not link.get('href'):
      # i can't believe this is in there
      if link.get('hre'):
        link['href'] = link.get('hre')
      continue
    make_url_replacements(link, 'href')
  for img in soup.find_all('img'):
    if not img.get('src'):
      continue
    make_url_replacements(img, 'src')
  for input_tag in soup.find_all('input'):
    if not input_tag.get('src'):
      continue
    make_url_replacements(input_tag, 'src')
  for script in soup.find_all('script'):
    if not script.get('src'):
      continue
    make_url_replacements(script, 'src')
  for link in soup.find_all('link'):
    if not link.get('href'):
      continue
    make_url_replacements(link, 'href')


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
    # else:
    #   print(f"couldn't find .{remove_class} to remove for {url}")

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

  search_script = soup.new_tag("script")
  search_script['charset'] = "utf-8"
  search_script['src'] = path_to_root + '/scripts/search.js'
  search_script['type'] = "text/javascript"
  soup.find('head').append(search_script)

  searchbox = soup.find('input', {'name': "search_phrase"})
  searchbox['onblur'] = ''
  searchbox['onclick'] = ''
  searchbox['id'] = 'search_box'
  searchbox['onkeydown'] = "searchKeyDown(event)"

  search_button = soup.find(class_='go_area').find('input')
  search_button['id'] = "search_button"
  search_button['onclick'] = "searchButtonClick()"

  if lang == "en":
    search_link = path_to_root + "/en/search"
  else:
    search_link = path_to_root + "/fr/recherche"
  soup.find(class_='right_column').find('a')['href'] = search_link

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
  images = (
    re.findall(r'url\(\/images\/(.+)\)', page_text) +
    re.findall(r'src=\"\/images\/(.+?)\"', page_text)
  )
  for img in images:
    if img not in downloaded_images:
      img_path = f"images/{img}"
      download_file(img_path)
      downloaded_images.add(img_path)

def scrape_userfiles(page_text):
  for file_name in re.findall(r'\/userfiles\/(.+?)"', page_text):
    file_path = f"userfiles/{file_name}"
    download_file(file_path)

def download_file(file_path):
  if file_path in known_missing_files:
    return
  if file_path in downloaded_files:
    return
  if file_path in downloaded_images:
    return

  last_slash = file_path.rfind("/")
  folder_path = f"./{file_path[:last_slash]}"
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)

  file_url = f"https://toolsofchange.com/{urllib.parse.quote(file_path)}"
  try:
    urllib.request.urlretrieve(file_url, f"./{file_path}")
  except Exception as e:
    print(f"couldn't find {file_path}")
    print(e)

  downloaded_files.add(file_path)


def generate_case_studies_homepage(page):
  if lang == "en":
    case_studies_home_url = "en/case-studies/"
  else:
    case_studies_home_url = "fr/etudes-de-cas/"
  os.makedirs(case_studies_home_url)
  with open(case_studies_home_url + "index.html", "x") as f:
    page_text = page.text
    page_text = page_text.replace(f'"/{case_studies_home_url}', '"./')
    def soup_adjuster(soup):
      # This is the "sort by latest, last 5 10 15" etc bar
      soup.find('div', class_="bar").decompose()
    generate_page(f, case_studies_home_url, page_text, soup_adjuster)

def soup_adjuster_to_remove_user_input(soup):
  # Remove "login to save plans" thing (top and bottom of page)
  for bar in soup.find_all('div', class_="bar"):
    bar.decompose()
  # This is where the user input would go if there were accounts
  for your_program_box in soup.find_all(class_="thickbox"):
    if your_program_box.find_previous("tr"):
      your_program_box.find_previous("tr").decompose();
    else:
      your_program_box.decompose()

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
    generate_page(f, url, page.text, soup_adjuster)

  guide_soup = BeautifulSoup(page.content, "html.parser")
  steps = guide_soup.find('div', id="steps_nav").find_all('a')
  for step in steps:
    url = cleanup_url(step['href'])
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      generate_page(f, url, page.text, soup_adjuster_to_remove_user_input)

def generate_tools_of_change():
  if lang == "en":
    url = "en/tools-of-change/"
  else:
    url = "fr/outils-de-changement/"

  page = requests.get("https://toolsofchange.com/" + url)
  os.makedirs(url)
  with open(url + "index.html", "x") as f:
    generate_page(f, url, page.text)

  tools_soup = BeautifulSoup(page.content, "html.parser")
  tool_links = tools_soup.find('div', class_="left_content").find_all('a')
  for tool in tool_links:
    url = cleanup_url(tool['href'])
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      generate_page(f, url, page.text, soup_adjuster_to_remove_user_input)


def cleanup_url(url):
  if url[0] == "/":
    url = url[1:]
  if url.startswith("http://www.toolsofchange.com/"):
    url = url[len("http://www.toolsofchange.com/"):]
  if url.startswith("http://toolsofchange.com/"):
    url = url[len("http://toolsofchange.com/"):]
  if url.startswith("https://toolsofchange.com/"):
    url = url[len("https://toolsofchange.com/"):]
  if url[-1] != "/":
    url += "/"
  url = url.replace("s%C3%A9curit%C3%A9-routi%C3%A8re", "securite-routiere")
  url = url.replace("m%C3%A9decine-du-travail", "medecine-du-travail")
  url = url.replace("efficacit%C3%A9-%C3%A9nerg%C3%A9tique", "efficacite-energetique")
  url = url.replace("Santé cardiovasculaire", "sante-cardiovasculaire")
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
    generate_page(f, topic_resource_url, page.text)

  # Generate pages for each of the topics
  homepage_soup = BeautifulSoup(page.content, "html.parser")
  resource_page_links = homepage_soup.find('div', class_="topic_resources_detail").find_all('a')
  for section in homepage_soup.find_all('div', class_="topic_resources_detail_pad"):
    resource_page_links = resource_page_links + section.find_all('a')

  resource_urls = [resource_page['href'] for resource_page in resource_page_links]

  if lang == "fr":
    resource_urls.append("/fr/ressources-de-sujets/la-medecine-du-travail/")
    resource_urls.append("/fr/ressources-de-sujets/detail/77/")
    resource_urls.append("/fr/ressources-de-sujets/detail/62/")
  else:
    resource_urls.append("/en/topic-resources/detail/329/")

  for url in resource_urls:
    url = cleanup_url(url)
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      # TODO(search): maybe remove the two advanced search boxes?
      generate_page(f, url, page.text)

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
          generate_page(f, url, page.text)


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
      generate_page(f, url, page.text, soup_adjuster)


def generate_simple_pages():
  if lang == "en":
    urls = [
      "en/contact-us/",
      "en/workshops/",
      "en/workshops/face-to-face/",
      "en/about-us/",
      "en/about-us/workbook-acknowledgements/",
      "en/landmark/",
      "en/help/", # TODO(post-backup): remove thing about creating an account
      "en/terms/",
      "en/program-impact-attribution/",
      "en/programs/community-based-social-marketing/",
      "en/programs/water-professionals/",
      "en/workshops/customized-webinar-based-presentations/",
      "en/topic-resources/energy-efficiency/landmark-case-studies-(energy)/",
      "en/topic-resources/transportation/landmark-case-studies-(transportation)/",
      "en/topic-resources/water-efficiency/water-links/",
    ]
  else:
    urls = [
      "fr/contactez-nous/",
      "fr/ateliers/",
      "fr/ateliers/présentations-personnalisé-par-webinaire/",
      "fr/au-sujet-de-nous/",
      "fr/au-sujet-de-nous/cahier-de-travail-/",
      "fr/aide/",
      "fr/modalités-d'utilisation/",
      "fr/programmes/le-marketing-social-communautaire/",
    ]

  for url in urls:
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      generate_page(f, url, page.text)

def generate_homepage():
  if lang == "en":
    url = "en/home/"
  else:
    url = "fr/accueil/"

  page = requests.get("https://toolsofchange.com/" + url)

  os.makedirs(url)
  with open(url + "index.html", "x") as f:
    def soup_adjuster(soup):
      # TODO(post-backup): put a hardcoded news section here
      soup.find('div', class_="latest_news_area").decompose()
      # Remove left margin now that the news is gone
      soup.find(attrs={'class':'webinar_area_wrap'})['style'] = "margin: 0;"
      for link in soup.find_all('a'):
        if "https://clicky.com" in link['href']:
          link.decompose()
    generate_page(f, url, page.text, soup_adjuster)

  homepage_soup = BeautifulSoup(page.content, "html.parser")
  for intro_link in homepage_soup.find('div', class_="intro_box").find_all('a'):
    url = cleanup_url(intro_link['href'])
    page = requests.get("https://toolsofchange.com/" + url)
    os.makedirs(url)
    with open(url + "index.html", "x") as f:
      generate_page(f, url, page.text)


def setup():
  print("setup")
  os.makedirs("./images/")
  os.makedirs("./public/images/")
  os.makedirs("./userfiles/Image")
  os.makedirs("./userfiles/File")
  generate_stylesheets()
  download_a_href_images()

# These are images that are linked to?? that are different images
# than the ones displayed on pages. Weird, but whatever we can also
# download them
def download_a_href_images():
  for img in [
    'images/documentimages/AIDS/PEP.gif',
    'images/documentimages/AQPortland/cartips.gif',
    'images/documentimages/AQPortland/prizedraw.gif',
    'images/documentimages/Ashland/bdtest.jpg',
    'images/documentimages/Ashland/housesign1.jpg',
    'images/documentimages/SparetheAir/SAsurvey.gif',
    'images/documentimages/U-PASS/generalad.gif',
    'images/documentimages/U-PASS/nightride.gif',
  ]:
    download_file(img)

def generate_english_site():
  global lang
  lang = "en"
  print("english")
  print("homepage")
  generate_homepage()
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
  print("simple pages")
  generate_simple_pages()

def generate_french_site():
  global lang
  lang = "fr"
  print("french")
  print("homepage")
  generate_homepage()
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
  print("simple pages")
  generate_simple_pages()

setup()
generate_english_site()
generate_french_site()
