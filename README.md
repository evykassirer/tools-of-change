# to create a full backup:

(1) remove old data: delete the folders `rm -r en/ fr/ public/ userfiles/ images/` (make sure to keep the search pages around to re-add them later) and the json files `rm case_study_data.json case_study_data_fr.json topic_resource_data.json`

(2) `python3 scrape_page_metadata.py` to regenerate the metadata for search

(3) `python3 create_backup.py` to generate the HTML files

(4) re-add search pages and rebuild search: `npx -y pagefind --site en` `npx -y pagefind --site fr`

To just re-scrape, but not fetch new metadata, you can keep the json files and not do step (2)


### Known errors:


homepage (same 7 pages in french) -- seems fine

```
couldn't find .sidebar_body to remove for en/home/
couldn't find .sidebar_body to remove for en/programs/community-economic-developers/
couldn't find .sidebar_body to remove for en/programs/environmental-promoters/
couldn't find .sidebar_body to remove for en/programs/health-promoters/
couldn't find .sidebar_body to remove for en/programs/safety/
couldn't find .sidebar_body to remove for en/programs/social-marketers/
couldn't find .sidebar_body to remove for en/programs/transportation-professionals/
```

case studies:

* can't find id in search results (english) 767-772 (the most recent ones)

missing ids for search results:

* 451-476
* 27
* 30
* 33
* 60
* 72
* 91
* 92
* 95
* 96
* 102
* 107-109
* 112
* 115
* 116
* 118
* 126
* 128
* 130
* 136
* 137
* 139
* 441
* 443-447

# search

* `npx -y pagefind --site en --serve` indexes the english pages

