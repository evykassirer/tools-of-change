import os
import requests
from bs4 import BeautifulSoup

# TODO
# - styling for case study pages
# - homepage


def generate_case_study_page(f, url):
  page = requests.get("https://toolsofchange.com/" + url)
  f.write(page.text)


def generate_stylesheets():
  stylesheet_path = "public/stylesheets/"
  if not os.path.exists(stylesheet_path):
      os.makedirs(stylesheet_path)
  for sheet in ["default", "tables", "print", "thickbox", "sortmenu"]:
    page = requests.get(f"https://toolsofchange.com/public/stylesheets/{sheet}.css")
    with open(f"public/stylesheets/{sheet}.css", "x") as f:
      f.write(page.text)



def main():
  URL = "https://toolsofchange.com/en/case-studies/?max=1000"
  page = requests.get(URL)

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
      generate_case_study_page(f, url)

main()
generate_stylesheets()
