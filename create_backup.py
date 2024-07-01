import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import re

# TODO
# - add the "tools of change" linked from the case study
# - make a proper homepage? after tools maybe
# - support french
# - search:
#     - topic, location, tool, landmark -- can scrape
#     - keyword -- this might be harder, but still important, can search the page content
# - case study pages: remove footer_left wrapper and put footer in parent wider div


def generate_page(f, url, page_text, path_to_root):
  scrape_images(page_text)

  page_text = page_text.replace("/public/", f"{path_to_root}/public/")
  page_text = page_text.replace("/userfiles/", f"{path_to_root}/userfiles/")
  # TODO: this might be temporary, but for now the home link goes to the case studies page
  page_text = page_text.replace("/en/home/", f"{path_to_root}/en/case-studies/")

  page_text = page_text.replace('href="/en/', f'href="{path_to_root}/en/')

  soup = BeautifulSoup(page_text,"html.parser")
  for remove_id in ["qnav", "nav_container"]:
    div = soup.find('div', id=remove_id)
    if div:
      div.decompose()
    else:
      print(f"couldn't find #{remove_id} to remove for {url}")
  for remove_class in ["sponsor_box", "intro_cap_top", "intro_cap_bottom", "footer_right", "sidebar_body"]:
    div = soup.find('div', class_=remove_class)
    if div:
      div.decompose()
    else:
      print(f"couldn't find .{remove_class} to remove for {url}")

  topic_ad = soup.find('img', class_="topic_ad")
  if topic_ad:
    topic_ad.parent.parent.decompose()
  else:
    print(f"couldn't find topic_ad for {url}")
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
  case_studies_home_url = "en/case-studies/"
  os.makedirs(case_studies_home_url)
  with open(case_studies_home_url + "index.html", "x") as f:
    page_text = page.text
    page_text = page_text.replace("/en/case-studies/", "./")
    generate_page(f, case_studies_home_url, page_text, "../..")

def generate_tools_pages():
  url = "en/tools-of-change/"
  page = requests.get("https://toolsofchange.com/" + url)
  if not os.path.exists(url):
      os.makedirs(url)
  with open(url + "index.html", "x") as f:
    generate_page(f, "en/tools-of-change/", page.text, "../..")

  for tool in [
    "building-motivation-over-time/",
    "feedback/",
    "financial-incentives-and-disincentives/",
    "norm-appeals/",
    # TODO add the rest
  ]:
    url = "en/tools-of-change/" + tool
    page = requests.get("https://toolsofchange.com/" + url)
    if not os.path.exists(url):
        os.makedirs(url)
    with open(url + "index.html", "x") as f:
      generate_page(f, url, page.text, "../../..")

      # TODO:
      # (1) remove .bar
      # (2) add two styles
      # left_content_2col {
      #   background: #e5edee;
      # }
      # .plan_col_right {
      #   display: none;
      # }

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


os.makedirs("./public/images/")
os.makedirs("./userfiles/Image")
URL = "https://toolsofchange.com/en/case-studies/?max=1000"
homepage = requests.get(URL)

generate_stylesheets()
generate_case_studies_homepage(homepage)
# generate_tools_pages()
generate_case_study_pages(homepage)
