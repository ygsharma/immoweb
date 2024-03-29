import scrapy
import json
import random

class ZimmoExtraction(scrapy.Spider):
    name = 'zimmo_extraction_spider'

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
        self.page_url = ""
        self.website_url = "https://www.zimmo.be/fr/heusden-3550/a-vendre/maison/K7RMV/"
        self.error = []


    def start_requests(self):

        yield scrapy.Request(
            url=self.website_url,
            callback=self.extract_data,
            headers=header,
            cb_kwargs={'header': header}
        )



    def extract_data(self, response, header):
        try:
            res = response.xpath('//script[contains(text(), "app.start")]/text()').get()
            if not len(res):
                with open(response.request.url.html, 'w') as f:
                    f.write(response.text())
        except:
            self.error.append(header['user-agent'])
            print(header['user-agent'])


        data = {}


        # listing details
        x = response.xpath('//section[@id="property-stats"]/div[@class="section-inner"]//div');
        for i in x:
            key = ' '.join(i.xpath('./div[2]//font/text()').getall())
            value = ' '.join(i.xpath('./div[1]//font/text()').getall())
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
        # documents = '//ul[@class="download-item-list"]/li/a'
        data['documents'] = response.xpath('//ul[@class="download-item-list"]//li/a/@href').getall()

        # construction block
        construction = response.xpath('//section[@id="construction"]//div[@class="info-list"]');
        for i in construction:
            key = ' '.join(i.xpath('.//div[@class="col-xs-7 info-name"]//font/text()').get(default='').strip().replace(' ','').lower())
            value = ' '.join(i.xpath('.//div[@class="col-xs-5 info-value"]//font/text()').get(default='').strip().replace(' ','').lower())
            if key:
                data[key] = value

        # description
        desc = response.xpath('//section[@id="description"]//text()').getall()
        x = ''
        for i in desc:
            if i.replace('\n', '').replace(' ', ''):
                x += i

        if x:
            data['description'] = x.strip().replace('\n', '')


        # json extraction
        start = res.index('property:') + 10
        end = res.index(';\n\n') - 1
        # modified_resp = res[start:end].replace(':', '":').replace(',')
        #
        # json_resp = json.loads()


        yield data;



