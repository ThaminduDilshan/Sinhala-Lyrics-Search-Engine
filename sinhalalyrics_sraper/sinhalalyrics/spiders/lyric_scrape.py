import scrapy
from sinhalalyrics.items import SinhalalyricsItem
from datetime import datetime
import re


## variables
artist_page_range = range(0,2)    # 0,1


class SinhalaLyrics(scrapy.Spider):
    name = 'sinhalasongbook_scraper'
    start_urls = ['https://sinhalasongbook.com/featured-artists-sinhala-song-book/#letA']

    def parse(self, response):
        count = 0
        for href in response.xpath("//div[contains(@class, 'entry-content')]/div[contains(@class, 'one-half first')]/p/a/@href"):
            url = href.extract()

            if count in artist_page_range:
                yield scrapy.Request(url, callback=self.parse_first_dir_contents)
            
            count += 1
            
    
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
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-3-6')]//span[contains(@class, 'entry-categories')]/a/text()").extract()
            item['artist'] = temp
        except:
            item['artist'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-3-6')]//span[contains(@class, 'entry-tags')]/a/text()").extract()
            item['genre'] = temp
        except:
            item['genre'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-2-6')]//span[contains(@class, 'lyrics')]/a/text()").extract()
            item['lyricWriter'] = temp
        except:
            item['lyricWriter'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-2-6')]//span[contains(@class, 'music')]/a/text()").extract()
            item['musicDirector'] = temp
        except:
            item['musicDirector'] = ''

        temp = response.xpath("//div[contains(@class, 'entry-content')]/h3/text()").extract()[0]
        temp = re.split('\|', temp)
        try:
            item['key'] = re.split(':', temp[0])[1].strip()
        except IndexError:
            item['key'] = temp[0].strip()
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
            item['views'] = None

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'nc_tweetContainer swp_share_button total_shares total_sharesalt')]/span[contains(@class, 'swp_count')]/text()").extract()[0]
            temp = int(re.sub('[^0-9,]', "", temp).replace(',', ''))
            item['shares'] = temp
        except:
            item['shares'] = None

        temp = response.xpath("//div[contains(@class, 'entry-content')]//pre/text()").extract()
        temp_lyric = ''
        for line in temp:
            line_content = re.sub( '  +', '\n', re.sub("[\d+^a-zA-Z|-|—|\[|\]]|\n|\t", "", line) )

            if '\n-' in line_content:
                pass
            else:
                temp_lyric += line_content

        item['lyric'] = temp_lyric

        yield item
