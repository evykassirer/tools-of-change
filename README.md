# to create a backup:

(1) remove old data: delete the folders [en, fr, userfiles, public] and the two json files

(2) `python3 scrape_page_metadata.py` to regenerate the list of case studies to scrape (TODO: add topic resources)

(3) `python3 create_backup.py` to generate the HTML files

(4) search! ********* look into this next


### Known errors:

stylesheets:

* couldn't find `public/images/transparent.gif` (it just doesn't exist)


homepage:

```
couldn't find .sidebar_body to remove for en/home/
couldn't find .sidebar_body to remove for en/programs/community-economic-developers/
couldn't find .sidebar_body to remove for en/programs/environmental-promoters/
couldn't find .sidebar_body to remove for en/programs/health-promoters/
couldn't find .sidebar_body to remove for en/programs/safety/
couldn't find .sidebar_body to remove for en/programs/social-marketers/
couldn't find .sidebar_body to remove for en/programs/transportation-professionals/
```

homepage french (same 7 pages):

```
couldn't find .sidebar_body to remove for fr/accueil/
couldn't find .sidebar_body to remove for fr/programmes/realisateurs-economiques-de-la-communauté/
couldn't find .sidebar_body to remove for fr/programmes/introduction-de-surete/
couldn't find .sidebar_body to remove for fr/programmes/professionnels-des-transports/
couldn't find .sidebar_body to remove for fr/programmes/instigateurs-de-sante/
couldn't find .sidebar_body to remove for fr/programmes/instigateurs-environnementaux/
couldn't find .sidebar_body to remove for fr/programmes/acheteurs-sociaux/
```

case studies:

* can't find id in search results (english) 767-772 (the most recent ones)


```
couldn't find userfiles/Image//Burlington%20map%203.PNG
couldn't find userfiles/Image/Street.jpg
couldn't find userfiles/Image//Chatham%20Area%20Map.JPG
couldn't find userfiles/Image//Andrew%20Bio%20Picture.jpg
```

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

