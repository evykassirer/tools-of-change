import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import re

# TODO
# - case study pages: remove footer_left wrapper and put footer in parent wider div
# - scrape full homepage
# - add the "tools of change" linked from the case study
# - support french


def generate_page(f, url, page_text, path_to_root):
  scrape_images(page_text)
  page_text = page_text.replace("/public/", f"{path_to_root}/public/")
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
  images = re.findall(r'url\(\/public\/images\/(.+)\)', page_text)
  for img in images:
    if img not in downloaded_images:
      download_image(img)
      downloaded_images.add(img)

  images = re.findall(r'url\(\.\.\/images\/(.+)\)', page_text)
  for img in images:
    if img not in downloaded_images:
      download_image(img)
      downloaded_images.add(img)

  images = re.findall(r'src=\"\/public\/images\/(.+?)\"', page_text)
  for img in images:
    if img not in downloaded_images:
      download_image(img)
      downloaded_images.add(img)

def download_image(image_name):
  imgURL = f"https://toolsofchange.com/public/images/{image_name}"
  try:
    urllib.request.urlretrieve(imgURL, f"./public/images/{image_name}")
  except Exception as e:
    print(f"couldn't find {image_name}")
    print(e)

def main():
  os.makedirs("./public/images/")
  URL = "https://toolsofchange.com/en/case-studies/?max=1000"
  page = requests.get(URL)

  case_studies_home_url = "en/case-studies/"
  os.makedirs(case_studies_home_url)
  with open(case_studies_home_url + "index.html", "x") as f:
    generate_page(f, case_studies_home_url, page.text, "../..")

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

main()
generate_stylesheets()
