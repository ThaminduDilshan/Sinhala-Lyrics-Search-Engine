# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SinhalalyricsItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    songName = scrapy.Field()
    artist = scrapy.Field()
    genre = scrapy.Field()
    lyricWriter = scrapy.Field()
    musicDirector = scrapy.Field()
    key = scrapy.Field()
    beat = scrapy.Field()
    views = scrapy.Field()
    shares = scrapy.Field()
    lyric = scrapy.Field()
