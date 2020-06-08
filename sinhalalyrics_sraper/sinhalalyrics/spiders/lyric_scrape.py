import scrapy
from sinhalalyrics.items import SinhalalyricsItem
from datetime import datetime
import re
from mtranslate import translate


## variables
exception_dict = {
    'Daddy': "ඩැඩී",
    'Wayo': "වායෝ"
}


def en_to_sn_translate(string):
    if string in exception_dict:
        return exception_dict[string]
    
    return translate(string, 'si', 'en')


def translate_array(stringList):
    temp = []
    for string in stringList:
        temp.append(en_to_sn_translate(string))
    
    return temp


class SinhalaLyrics(scrapy.Spider):
    name = 'sinhalasongbook_scraper'
    start_urls = ['https://sinhalasongbook.com/all-sinhala-song-lyrics-and-chords/?_page=' + str(i) for i in range(1,2)]            # max range(1, 23)

    def parse(self, response):
        for href in response.xpath("//main[contains(@id, 'genesis-content')]//div[contains(@class, 'entry-content')]//div[contains(@class, 'pt-cv-wrapper')]//h4[contains(@class, 'pt-cv-title')]/a/@href"):
            url = href.extract()

            yield scrapy.Request(url, callback=self.parse_dir_contents)
    

    def parse_dir_contents(self, response):
        item = SinhalalyricsItem()

        temp = response.xpath("//div[contains(@class, 'site-inner')]//header[contains(@class, 'entry-header')]/h1/text()").extract()[0]
        temp = re.split('\||–', temp)
        item['songName'] = temp[1].strip()

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-3-6')]//span[contains(@class, 'entry-categories')]/a/text()").extract()
            temp = translate_array(temp)
            item['artist'] = temp
        except:
            item['artist'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-3-6')]//span[contains(@class, 'entry-tags')]/a/text()").extract()
            temp = translate_array(temp)
            item['genre'] = temp
        except:
            item['genre'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-2-6')]//span[contains(@class, 'lyrics')]/a/text()").extract()
            temp = translate_array(temp)
            item['lyricWriter'] = temp
        except:
            item['lyricWriter'] = ''

        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-2-6')]//span[contains(@class, 'music')]/a/text()").extract()
            temp = translate_array(temp)
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
            line_content = line_content.replace('∆', '')
            line_content = line_content.replace('#', '')

            if '\n-' in line_content:
                pass
            else:
                temp_lyric += line_content

        item['lyric'] = temp_lyric

        yield item
