import requests
from bs4 import BeautifulSoup

def new_url(base_url, new_url):
  base_url = base_url.strip()
  new_url = new_url.strip()
  if new_url[0] == "/":
    return f"http://127.0.0.1:8000{new_url}"

  orig_base_url = base_url[:]
  orig_new_url = new_url[:]
  if base_url[-1] == "/":
    base_url = base_url[:-1]
  while new_url[:3] == "../":
    last_slash = base_url.rfind("/")
    # like en/programs/social-marketers/#2-3
    if last_slash+1 < len(base_url) and base_url[last_slash+1] == "#":
      base_url = base_url[:last_slash]
      continue
    # some urls have two slashes in them...
    if base_url[last_slash-1] == "/":
      base_url = base_url[:last_slash-1]
    else:
      base_url = base_url[:last_slash]
    new_url = new_url[3:]
  if new_url[:2] == "./":
    new_url = new_url[2:]
  ret = base_url + "/" + new_url

  return ret

nonexisting_pages = set()
known_missing_pages = [
  'en/tools-of-change/peer/',
  'en/case-studies/detail/157',
  'en/case-studies/detail/158',
  'en/case-studies/detail/159',
  'en/case-studies/detail/176',
  'en/case-studies/detail/91',
  'en/case-studies/detail/736',
  'fr/etudes-de-cas/detail/100',
  'fr/etudes-de-cas/detail/111',
  'fr/etudes-de-cas/detail/114',
  'fr/etudes-de-cas/detail/129',
  'fr/etudes-de-cas/detail/439',
  'fr/etudes-de-cas/detail/87',
  'fr/programmes/water-transport-(english-only)/',
]


def check_page_exists(url):
  if url in nonexisting_pages:
    return False
  for file in known_missing_pages:
    if file in url:
      return False
  page = requests.get(url)
  if page.status_code == 404:
    nonexisting_pages.add(url)
    return False
  return True

def alter_page(url):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")

  for link in soup.find_all('a'):
    # wow there's some bad html in here
    if not link.get('href'):
      continue
    href = link['href']
    # not toc
    if href[0] != "/" and href[0] != ".":
      continue

    full_url = new_url(url, href)
    if full_url in visited_urls:
      continue
    visited_urls.add(full_url)

    if (
      not check_page_exists(full_url)
      or full_url[-4:] in [".pdf", ".doc", ".mp3", ".png", ".JPG", ".jpg", ".gif"]
      or full_url == "http://127.0.0.1:8000/"
    ):
      continue

    queue.append(full_url)

  change_made = False
  for img in soup.find_all('img'):
    src = img['src']
    if src.startswith("/images"):
      img['src'] = url_relative_path_to_home(url) + src
      print("fixing image source")
      change_made = True

  if '<span data-pagefind-filter="Resource type' not in str(soup):
    resource_type = None
    if "topic-resources/detail" in url or "ressources-de-sujets/detail" in url:
      resource_type = "Topic Resource"
    elif "case-studies/detail" in url or "etudes-de-cas/detail" in url:
      resource_type = "Case Study"
    if resource_type:
      new_tag = soup.new_tag("span")
      new_tag['style'] = "display: none;"
      new_tag['data-pagefind-filter'] = f"Resource type: {resource_type}"
      soup.find("body").append(new_tag)
      print("adding basic resource type")
      change_made = True


  if "topic-resources/detail" in url or "ressources-de-sujets/detail" in url:
    for tr in soup.find_all('tr'):
      if tr.find(class_='highlight_box') and tr.find(class_='highlight_box').text in ["Catégorie:", "Resource Type:"]:
        for resource_type in tr.find(class_='rt_text_box').text.split(","):
          if resource_type.strip().lower() == "":
            continue
          full_resource_type = f"Resource type: Topic Resource: {resource_type.strip().lower()}"
          if f'<span data-pagefind-filter="{full_resource_type}' not in str(soup):
            new_tag = soup.new_tag("span")
            new_tag['style'] = "display: none;"
            new_tag['data-pagefind-filter'] = full_resource_type
            soup.find("body").append(new_tag)
            # print("adding advanced resource type")
            change_made = True


  if change_made:
    with open(relative_url(url) + "index.html", "w") as f:
      f.write(str(soup))



def relative_url(url):
  if url.startswith("http://www.toolsofchange.com/"):
    url = url[len("http://www.toolsofchange.com/"):]
  if url.startswith("http://toolsofchange.com/"):
    url = url[len("http://toolsofchange.com/"):]
  if url.startswith("https://toolsofchange.com/"):
    url = url[len("https://toolsofchange.com/"):]
  if url.startswith("http://127.0.0.1:8000/"):
    url = url[len("http://127.0.0.1:8000/"):]
  if url[0] == "/":
    url = url[1:]
  if url[-1] != "/":
    url += "/"
  return url

def url_relative_path_to_home(url):
  url = relative_url(url)
  return "/".join([".." for n in range(url.count("/"))])

visited_urls = set();
queue = []

def alter_pages():
  queue.append("http://127.0.0.1:8000/en/home/")
  i = 0
  while len(queue):
    url = queue.pop(0)
    url = url.strip()
    alter_page(url)
    i += 1
    if i % 100 == 0:
      print(f"{i} pages checked so far\n")
  print("🍄 all done\n")


alter_pages()
