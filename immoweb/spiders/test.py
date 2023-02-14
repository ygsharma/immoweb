import json
import re

import scrapy
import random

class zimmo_web(scrapy.Spider):
    name = 'zimmo_web_spider'
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/110.0.5481.83 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/110.0.5481.83 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.63 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.63 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.63 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; LM-Q710(FGN)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.63 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13.2; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/109.0 Mobile/15E148 Safari/605.1.15',
        'Mozilla/5.0 (iPad; CPU OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/109.0 Mobile/15E148 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def start_requests(self):
        # first page url
        header = {'user-agent': random.choice(zimmo_web.user_agents)}
        url = 'https://zimmo.be/fr/rechercher/?search=eyJmaWx0ZXIiOnsic3RhdHVzIjp7ImluIjpbIkZPUl9TQUxFIiwiVEFLRV9PVkVSIl19LCJjYXRlZ29yeSI6eyJpbiI6WyJIT1VTRSIsIkFQQVJUTUVOVCJdfX19'
        yield scrapy.Request(
            url=url,
            headers=header,
            callback=self.get_pages
        )

    def get_pages(self, response):
        # extract no of total pages
        # total_pages = int(response.xpath('//ul[@class="dropdown-menu inner selectpicker"]//li[last()]//span/text()').get())

        # extract the base64 code of 2'nd page url, parameter &p=<1, 2, 3>
        page = response.xpath('//a[contains(@href, "p=2")]/@href').get()

        # generate the url's for all pages up till total no of pages
        for i in range(2, 100+1):
            header = {'user-agent': random.choice(zimmo_web.user_agents)}
            s = '&p=' + str(i)
            page_url = page.replace('&p=2', s)

        # call on all those urls
            yield scrapy.Request(
                url=page_url,
                callback=self.extract_listings,
                headers=header
            )



    def extract_listings(self, response):

        # extract all the listing urls
        listing_url = response.xpath('//div[@class="property-item_title "]//a/@href').getall()

        # call on those listing urls to get the data
        for i in listing_url:
            header = {'user-agent': random.choice(zimmo_web.user_agents)}
            yield scrapy.Request(
                url='https://www.zimmo.be' + i,
                callback=self.extract_data,
                headers=header
            )


    def convert_to_json(data):
        data = data.replace(' ', '').replace('\n', '')
        json_data = re.findall('property:(.*?)(\);)', data)[0][0]
        regex = r'(,|{|})([a-z].*?)(:)'
        json_data = '{"property": ' + re.sub(regex, lambda x: x.group(1) + '"' + x.group(2).strip() + '"' + x.group(3), json_data).replace("'", '"')
        json_data = re.sub('(.)(,)(})', lambda x: x.group(1) + x.group(3), json_data)
        return json.loads(json_data)

    def extract_data(self, response):
        # data point extraction
        try:
            res = response.xpath('//script[contains(text(), "uuid")]/text()').get()
            # if not len(res):
            #     with open(response.request.url.html, 'w') as f:
            #         f.write(response.text())
        except:
            print('Extract data error')

        data = {}


        # listing details
        x = response.xpath('//section[@id="property-stats"]/div[@class="section-inner"]//div');
        for i in x:
            key = ' '.join(i.xpath('./div[2]/text()').getall())
            value = ' '.join(i.xpath('./div[1]/text()').getall())
            if key:
                data[key] = value


        # feature pairs
        li = response.xpath('//section[@id="main-features"]//ul[@class="main-features"]/li');
        for i in li:
            key = ' '.join(i.xpath('./strong/text()').get(default='').strip().replace(' ','').lower())
            value = ' '.join(i.xpath('./span/text()').get(default='').strip().replace(' ','').lower())
            if key:
                data[key] = value;



        # documents block
        data['documents'] = response.xpath('//ul[@class="download-item-list"]//li//a/@href').getall()

        # construction block
        construction = response.xpath('//section[@id="construction"]//div[@class="info-list"]');
        for i in construction:
            key = ' '.join(i.xpath('.//div[@class="col-xs-7 info-name"]/text()').get(default='').strip().replace(' ','').lower())
            value = ' '.join(i.xpath('.//div[@class="col-xs-5 info-value"]/text()').get(default='').strip().replace(' ','').lower())
            if key:
                data[key] = value

        # description
        desc = response.xpath('//section[@id="description"]//div/text()').getall()
        x = ''
        for i in desc:
            if i.replace('\n', '').replace(' ', ''):
                x += i

        if x:
            data['description'] = x.strip().replace('\n', '')


        # json extraction
        if res:
            json_dict = self.convert_to_json(res)
            data['uuid'] = json_dict['uuid']



        yield data;


