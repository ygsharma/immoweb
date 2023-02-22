import json
import random
import re

import scrapy


# function to convert he json
def convert_to_json(data):
    data = data.replace(' ', '').replace('\n', '')
    json_data = re.findall('property:(.*?)(\);)', data)[0][0]
    regex = r'(,|{|})([a-z].*?)(:)'
    json_data = '{"property": ' + re.sub(regex, lambda x: x.group(1) + '"' + x.group(2).strip() + '"' + x.group(3),
                                         json_data).replace("'", '"')
    json_data = re.sub('(.)(,)(})', lambda x: x.group(1) + x.group(3), json_data)
    return json.loads(json_data)


def cleaner(text):
    text = text.replace('\n', '')
    text = ' '.join(text.split())
    return text


user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13.2; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'
]


class zimmo_web(scrapy.Spider):
    name = 'zimmo_web_spider'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_requests(self):
        # first page url
        header = {'user-agent': random.choice(user_agents)}
        url = 'https://zimmo.be/fr/rechercher/?search=eyJmaWx0ZXIiOnsic3RhdHVzIjp7ImluIjpbIkZPUl9TQUxFIiwiVEFLRV9PVkVSIl19LCJjYXRlZ29yeSI6eyJpbiI6WyJIT1VTRSIsIkFQQVJUTUVOVCJdfX19'
        yield scrapy.Request(
            url=url,
            headers=header,
            callback=self.get_pages
        )

    def get_pages(self, response):
        # extract no of total pages
        total_pages = int(
            response.xpath('//ul[@class="dropdown-menu inner selectpicker"]//li[last()]//span/text()').get())

        # extract the base64 code of 2'nd page url, parameter &p=<1, 2, 3>
        page = response.xpath('//a[contains(@href, "p=2")]/@href').get()

        # generate the url's for all pages up till total no of pages
        for i in range(2, total_pages + 1):
            header = {'user-agent': random.choice(user_agents)}
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
            header = {'user-agent': random.choice(user_agents)}
            yield scrapy.Request(
                url='https://www.zimmo.be' + i,
                callback=self.extract_data,
                headers=header
            )

    def extract_data(self, response):
        # data point extraction
        try:
            res = response.xpath('//script[contains(text(), "uuid")]/text()').get()
            json_data = convert_to_json(res)
        except:
            print('Extract data error')
            exit()

        data = {}

        # upper block
        # no of views
        # TODO : API

        data['favorite_property'] = cleaner(response.xpath('//div[@class="stat-block  favorites"]/div[@class="stat-text text"]/text()').get(''))
        data['days_on_zimmo'] = cleaner(response.xpath('//div[@class="stat-block days-on-zimmo"]/div/text()').get(''))
        data['last_modification'] = cleaner(response.xpath('//div[@class="stat-block last-update"]/div/text()').get(''))

        # first block
        data['street'] = json_data['property'].get('straat', '')
        data['street_number'] = json_data['property'].get('nummer', '')
        data['local_authority'] = json_data['property'].get('gemeente', '')
        data['postal_code'] = json_data['property'].get('postcode', '')
        data['latitude'] = json_data['property'].get('lat', '')
        data['longitude'] = json_data['property'].get('lon', '')
        data['price'] = json_data['property'].get('prijs', '')
        data['property_type'] = json_data['property'].get('type', '')
        data['property_sub_type'] = json_data['property'].get('subtype', '')
        data['property_code'] = json_data['property'].get('code', '')
        data['bedrooms'] = json_data['property'].get('aantal_slaapkamers', '')
        data['heating'] = json_data['property'].get('verwarming', '')
        data['living_area'] = json_data['property'].get('woonopp', '')
        data['ground_area'] = json_data['property'].get('grondopp', '')
        data['construction_year'] = json_data['property'].get('bouwjaar', '')
        data['construction_type'] = json_data['property'].get('constructionType', '')
        data['year_of_renovation'] = json_data['property'].get('renovatiejaar', '')
        data['new_building'] = json_data['property'].get('nieuwbouw', '')


        data['epc'] = json_data['property'].get('epc', '')
        data['energy_label_category'] = json_data['property'].get('energyLabelCategory', '')
        data['cadastral_income'] = json_data['property'].get('cadastralIncome', '')
        data['plot_cost'] = json_data['property'].get('plot_cost', '')
        data['taxable_by_6'] = json_data['property'].get('taxableBy6', '')
        data['taxable_by_12'] = json_data['property'].get('taxableBy12', '')
        data['popularity'] = json_data['property'].get('popularity', '')
        data['mobi_score'] = json_data['property'].get('mobiScore', '')
        data['zmv_price'] = json_data['property'].get('zmvPrice', '')
        data['virtual_visit'] = json_data['property'].get('virtueel_bezoek', '')
        data['video_url'] = json_data['property'].get('videoUrl', '')
        data['construction_state'] = json_data['property'].get('constructionState', '')
        data['title'] = json_data['property'].get('title', '')
        data['boosted'] = json_data['property'].get('boosted', '')
        data['corona_direct'] = json_data['property'].get('coronaDirect', '')
        data['province'] = json_data['property'].get('province', '')
        data['video_url'] = json_data['property'].get('videoUrl', '')
        data['video_url'] = json_data['property'].get('videoUrl', '')
        data['video_url'] = json_data['property'].get('videoUrl', '')
        data['video_url'] = json_data['property'].get('videoUrl', '')
        data['video_url'] = json_data['property'].get('videoUrl', '')
        data['video_url'] = json_data['property'].get('videoUrl', '')
        data['video_url'] = json_data['property'].get('videoUrl', '')
        data['video_url'] = json_data['property'].get('videoUrl', '')

        # advertiser info
        data['advertiser_name'] = json_data['property']['advertiser'].get('name', '')
        data['advertiser_phone'] = json_data['property']['advertiser'].get('phone', '')
        data['advertiser_mobile'] = json_data['property']['advertiser'].get('mobile', '')

        # sold_online
        data['notary_name'] = json_data['property']['notary']['type'].get('name', '')
        data['start_date'] = json_data['property']['notary']['interactiveSale'].get('startDate', '')
        data['deadline'] = json_data['property']['notary']['interactiveSale'].get('endDate', '')
        data['bidding_bracket'] = json_data['property']['notary']['interactiveSale'].get('increment', '')




        data['address'] = cleaner(response.xpath('//h2[@class="section-title __full-address"]/span/text()').get(''))


        #

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
            key = ' '.join(i.xpath('./strong/text()').get(default='').strip().replace(' ', '').lower())
            value = ' '.join(i.xpath('./span/text()').get(default='').strip().replace(' ', '').lower())
            if key:
                data[key] = value;

        # documents block
        data['documents'] = response.xpath('//ul[@class="download-item-list"]//li//a/@href').getall()

        # construction block
        construction = response.xpath('//section[@id="construction"]//div[@class="info-list"]');
        for i in construction:
            key = ' '.join(
                i.xpath('.//div[@class="col-xs-7 info-name"]/text()').get(default='').strip().replace(' ', '').lower())
            value = ' '.join(
                i.xpath('.//div[@class="col-xs-5 info-value"]/text()').get(default='').strip().replace(' ', '').lower())
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

        yield data
