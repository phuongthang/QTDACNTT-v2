# FbCrawlerDevC

A simple Facebook Crawler to crawl data including post and comments from Facebook

## Configure
Change URI Database in settings.py

## How to use
Use the format following format command:
scrapy crawl fb -a email="" -a password="" -a page="" -a date="" -a lang="" -a keyword=""
where:
- email & password is the Facebook accout, 
- page is the name from URL of the page (for example: https://www.facebook.com/teammonsterbox, then the page is "teammonsterbox")
- lang is the language, currently "en" available
- date is the date from that the crawler craw data up to now
- keyword is the word that the post must contains to be crawled, if not leave it blank or don't inlucde it in the command

## Reference
This is a customized version that is based on https://github.com/rugantio/fbcrawl for personal purposes only.
