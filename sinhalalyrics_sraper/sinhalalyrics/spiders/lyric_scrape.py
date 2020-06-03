import scrapy
from sinhalalyrics.items import SinhalalyricsItem
from datetime import datetime
import re

class SinhalaLyrics(scrapy.Spider):
    name = 'sinhalasongbook_scraper'

    start_urls = ['https://sinhalasongbook.com/featured-artists-sinhala-song-book/#letA']

    def parse(self, response):
        for href in response.xpath("//div[contains(@class, 'entry-content')]/div[contains(@class, 'one-half first')]/p/a/@href"):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_first_dir_contents)

    
    def parse_first_dir_contents(self, response):
        for href in response.xpath("//main[contains(@id, 'genesis-content')]//div[contains(@class, 'articles')]//h2[contains(@class, 'entry-title')]/a[contains(@class, 'entry-title-link')]/@href"):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_second_dir_contents)


    def parse_second_dir_contents(self, response):
        item = SinhalalyricsItem()

        temp = response.xpath("//div[contains(@class, 'entry-content')]/h2/text()").extract()[0]
        temp = re.split('\||–', temp)
        item['songName'] = temp[1].strip()

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-3-6')]//span[contains(@class, 'entry-categories')]/a/text()").extract()[0]
            item['artist'] = temp.strip()
        except:
            item['artist'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-3-6')]//span[contains(@class, 'entry-tags')]/a/text()").extract()
            item['genre'] = temp
        except:
            item['genre'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-2-6')]//span[contains(@class, 'lyrics')]/a/text()").extract()[0]
            item['lyricWriter'] = temp.strip()
        except:
            item['lyricWriter'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-2-6')]//span[contains(@class, 'music')]/a/text()").extract()[0]
            item['musicDirector'] = temp.strip()
        except:
            item['musicDirector'] = ''

        temp = response.xpath("//div[contains(@class, 'entry-content')]/h3/text()").extract()[0]
        temp = re.split('\|', temp)
        try:
            item['key'] = re.split(':', temp[0])[1].strip()
        except:
            item['key'] = temp.strip()
            item['beat'] = ''
        try:
            item['beat'] = re.split(':', temp[1])[1].strip()
        except:
            item['beat'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]/div[contains(@class, 'tptn_counter')]/text()").extract()[0]
            temp = int(re.sub('[^0-9,]', "", temp).replace(',', ''))
            item['views'] = temp
        except:
            item['views'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'nc_tweetContainer swp_share_button total_shares total_sharesalt')]/span[contains(@class, 'swp_count')]/text()").extract()[0]
            temp = int(re.sub('[^0-9,]', "", temp).replace(',', ''))
            item['shares'] = temp
        except:
            item['shares'] = ''

        temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-row')]//div[contains(@class, 'su-column-inner su-u-clearfix su-u-trim')]/pre/text()").extract()[0]
        temp_lyric = ''
        for line in temp:
            temp_lyric += re.sub( '  +', '\n', re.sub("[\d+^a-zA-Z|-]|\n", "", line) )

        item['lyric'] = temp_lyric

        yield item
