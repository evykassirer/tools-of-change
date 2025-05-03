# to create a full backup:

(1) remove old data: delete the folders [en, fr, userfiles, public] and the two json files

(2) `python3 scrape_page_metadata.py` to regenerate the list of case studies to scrape (TODO: add topic resources to metadata)

(3) `python3 create_backup.py` to generate the HTML files

(4) search! ********* look into this next

To just re-scrape, but not fetch new metadata, you can keep the json files and not do step (2)


### Known errors:

stylesheets:

* couldn't find `public/images/transparent.gif` (it just doesn't exist)


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


missing files:

* couldn't find public/images/transparent.gif
* couldn't find userfiles/Virgin Atlantic&#8217;s Airline Captains Improve Fuel Efficiency -2021-12-16(1).pdf
* couldn't find userfiles/Image/Star%20Party.png
* couldn't find userfiles/File//ClimateSmart%20Case%20Study%20FINAL2.pdf
* couldn't find userfiles/File//Handout_TOC_Highlights_2012_03_01_2pp.pdf
  * [Errno 2] No such file or directory: './userfiles/File//Handout_TOC_Highlights_2012_03_01_2pp.pdf'
* couldn't find userfiles/Image//Burlington%20map%203.PNG
* couldn't find userfiles/CrugerK_TOC_TC_EN_2010_02_23_2pp.pdf
* couldn't find userfiles/CrugerK_TOC_TC_EN_2010_02_23_6pp.pdf
* couldn't find userfiles/Image/Street.jpg
* couldn't find userfiles/Smart Commute Q4 Report print.pdf
* couldn't find userfiles/Image//Chatham%20Area%20Map.JPG
* couldn't find userfiles/Image//Chatham%20Area%20Map.JPG
* couldn't find userfiles/File//UGA%20Recycling%20Bin%20Feedback.pdf
* couldn't find userfiles/Handouts%20-%20May%209%20-2013.pdf
* couldn't find userfiles/Image//Andrew%20Bio%20Picture.jpg
* couldn't find userfiles/Q&amp;A.pdf
* couldn't find userfiles/Smarter Travel Case Handout2.pdf
