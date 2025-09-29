import requests
from bs4 import BeautifulSoup

""" progress
381 404s by 900
949 total


89, 906 checked total

--

74, 908 total

--

35 404s, 934 checked total (july 15)

--

9 404s, 936 checked total (july 16)

--

7 404s, 936 checked total (july 16)

--

july 17:
938 pages checked
not toc urls: 990
pages that have 404'd: 2

"""

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

  # if "fr/en/" in ret:
  #   print(f"fr en {ret} made for {orig_base_url} to {orig_new_url}")
  if "en/en" in ret:
    print(f"double en {ret} made for {orig_base_url} to {orig_new_url}")
  if "fr/fr" in ret:
      print(f"double fr {ret} made for {orig_base_url} to {orig_new_url}")
  # if "//" in ret[10:]:
  #   print(f"double slash {ret} made for {orig_base_url} to {orig_new_url}")
  return ret

"""
>>> new_url("www.test.com/hello/friend", "../enemy")
'www.test.com/hello/enemy'

>>> new_url("www.test.com/hello/friend", "./enemy")
'www.test.com/hello/friend/enemy'

>>> new_url("www.test.com", "enemy")
'www.test.com/enemy'

>>> new_url("www.test.com", "./enemy")
'www.test.com/enemy'
"""


nonexisting_pages = set()

# This should ideally import from create_back.py but whatever
known_missing_files = [
  'public/images/transparent.gif', # this one doesn't matter
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
  'fr/etudes-de-cas/detail/82',
  'fr/etudes-de-cas/detail/87',
  'fr/programmes/water-transport-(english-only)/',
]


def check_page_exists(url):
  if url in nonexisting_pages:
    return False
  for file in known_missing_files+known_missing_pages:
    if file in url:
      return False
  page = requests.get(url)
  if page.status_code == 404:
    nonexisting_pages.add(url)
    return False
  return True

def check_page(url):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")

  for link in soup.find_all('a'):
    # wow there's some bad html in here
    if not link.get('href'):
      continue
    href = link['href']
    if href in not_toc:
      continue
    if href[0] != "/" and href[0] != ".":
      not_toc.add(href)
      continue
    full_url = new_url(url, href)
    if full_url in checked_urls:
      continue
    if check_page_exists(full_url) and full_url[-4:] not in [".pdf", ".doc", ".mp3", ".png", ".JPG", ".jpg", ".gif"]:
      if full_url == "http://127.0.0.1:8000/":
        continue
      queue.append(full_url)
    checked_urls.add(full_url)

  for img in soup.find_all('img'):
    src = img['src']
    if src in not_toc:
      continue
    if src[0] != "/" and src[0] != ".":
      not_toc.add(src)
      continue
    full_url = new_url(url, src)
    if full_url in checked_urls:
      continue
    check_page_exists(full_url)
    checked_urls.add(full_url)
    # no need to add to queue since it's just an image source


checked_urls = set();
not_toc = set()
queue = []

def check_complete_backup():
  queue.append("http://127.0.0.1:8000/en/home/")
  i = 0
  while len(queue):
    url = queue.pop(0)
    url = url.strip()
    check_page(url)
    i += 1
    if i % 100 == 0:
      print(i)
      print(f"not toc urls: {len(not_toc)}")
      print(f"pages that have 404'd: {len(nonexisting_pages)}")
      print("\n")
  print("🍄 all done")
  print(f"{i} pages checked")
  print(f"not toc urls: {len(not_toc)}")
  print(f"pages that have 404'd: {len(nonexisting_pages)}")
  print("\n")

def print_not_toc():
  print("\n\nnot TOC?")
  for url in not_toc:
    if url[0] == "?":
      continue
    if url[0] == "#":
      continue
    if url[:6] == "mailto":
      continue
    print(url)

def print_404s():
  print("❌ 404: ")
  for url in sorted(list(nonexisting_pages)):
    print(url)


check_complete_backup()

print_404s()
# print_not_toc()