import scrapy
from sinhalalyrics.items import SinhalalyricsItem
from datetime import datetime
import re
from mtranslate import translate
import pickle


## variables
exception_dict = {
    'Daddy': "ඩැඩී",
    'Wayo': "වායෝ"
}
translated_dict = {}            # dictionary lookup to avoid translate failures and speedup process


def en_to_sn_translate(string):
    if string in exception_dict:
        return exception_dict[string]
    elif string in translated_dict:
        return translated_dict[string]
    elif string.lower() == "unknown":
        return ''
    else:
        translated = translate(string, 'si', 'en')
        translated_dict[string] = translated
        return translated


def translate_array(stringList):
    temp = []
    for string in stringList:
        temp.append(en_to_sn_translate(string))
        
        # if string in ['', None]:
        #     pass
        # if string.lower() == "unknown":
        #     pass
        # else:
        #     temp.append(string)
    
    return temp


class SinhalaLyrics(scrapy.Spider):
    name = 'sinhalasongbook_scraper'
    start_urls = ['https://sinhalasongbook.com/all-sinhala-song-lyrics-and-chords/?_page=' + str(i) for i in range(1,2)]            # max range(1, 23)

    def parse(self, response):
        global translated_dict

        try:
            translated_dict = pickle.load(open('../translated_dict.pickle', 'rb'))
        except (OSError, IOError):
            pickle.dump(translated_dict, open('../translated_dict.pickle', 'wb'))

        for href in response.xpath("//main[contains(@id, 'genesis-content')]//div[contains(@class, 'entry-content')]//div[contains(@class, 'pt-cv-wrapper')]//h4[contains(@class, 'pt-cv-title')]/a/@href"):
            url = href.extract()

            yield scrapy.Request(url, callback=self.parse_dir_contents)
    

    def parse_dir_contents(self, response):
        global translated_dict

        item = SinhalalyricsItem()

        item['url'] = response.url

        # song name
        temp = response.xpath("//div[contains(@class, 'site-inner')]//header[contains(@class, 'entry-header')]/h1/text()").extract()[0]
        temp = re.split('\||–|-', temp)
        item['songName'] = temp[1].strip()

        # artist name
        temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-3-6')]//span[contains(@class, 'entry-categories')]/a/text()").extract()
        if len(temp) == 0:
            item['artist'] = []
        else:
            temp = translate_array(temp)
            item['artist'] = temp
        
        # genre
        temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-3-6')]//span[contains(@class, 'entry-tags')]/a/text()").extract()
        if len(temp) == 0:
            item['genre'] = []
        else:
            temp = translate_array(temp)
            item['genre'] = temp
        
        # lyric writer
        temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-2-6')]//span[contains(@class, 'lyrics')]/a/text()").extract()
        if len(temp) == 0:
            item['lyricWriter'] = []
        else:
            temp = translate_array(temp)
            item['lyricWriter'] = temp

        # music director
        temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'su-column su-column-size-2-6')]//span[contains(@class, 'music')]/a/text()").extract()
        if len(temp) == 0:
            item['musicDirector'] = []
        else:
            temp = translate_array(temp)
            item['musicDirector'] = temp

        # key & beat
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

        # no of views
        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]/div[contains(@class, 'tptn_counter')]/text()").extract()[0]
            temp = int(re.sub('[^0-9,]', "", temp).replace(',', ''))
            item['views'] = temp
        except:
            item['views'] = None

        # no of shares
        try:
            temp = response.xpath("//div[contains(@class, 'entry-content')]//div[contains(@class, 'nc_tweetContainer swp_share_button total_shares total_sharesalt')]/span[contains(@class, 'swp_count')]/text()").extract()[0]
            temp = int(re.sub('[^0-9,]', "", temp).replace(',', ''))
            item['shares'] = temp
        except:
            item['shares'] = None

        # lyric
        temp = response.xpath("//div[contains(@class, 'entry-content')]//pre/text()").extract()
        temp_lyric = ''
        new_line_found_1 = True
        new_line_found_2 = False

        for line in temp:
            line_content = (re.sub("[\da-zA-Z\-—\[\]\t\@\_\!\#\+\$\%\^\&\*\(\)\<\>\?\|\}\{\~\:\∆\/]", "", line)).split('\n')
            
            for lline in line_content:
                if lline == '' or lline.isspace():
                    if not new_line_found_2:
                        new_line_found_2 = True
                        temp_lyric += '\n'
                else:
                    new_line_found_1 = False
                    new_line_found_2 = False
                    temp_lyric += lline.strip()
            
            if not new_line_found_1:
                new_line_found_1 = True
                temp_lyric += '\n'

        item['lyric'] = temp_lyric

        pickle.dump(translated_dict, open('../translated_dict.pickle', 'wb'))

        yield item
