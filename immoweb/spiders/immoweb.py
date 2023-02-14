import scrapy
import json
from scrapy.crawler import CrawlerProcess
import copy

class ImmowebExtraction(scrapy.Spider):
    name = "immoweb_extraction_spider"

    # extract all the ids
    # call on these ids from the data of property
    # extract data points from the property's page

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page_url = "https://www.immoweb.be/en/search-results?page={}"
        self.website_url = "https://immoweb.be"


    def start_requests(self):
        yield scrapy.Request(url=self.website_url,
                             callback=self.login)

    def login(self, response):
        xsrf = response.headers.getlist('Set-Cookie')[0].decode("utf-8").split(";")[0].split("=")[1]
        immoweb_session = response.headers.getlist('Set-Cookie')[1].decode("utf-8").split(";")[0].split("=")[1]
        url = 'https://www.immoweb.be/en/login'
        payload = '{\"login-email\":\"thelouiswills4@gmail.com\",\"login-password\":\"Rock0004@\"}'
        headers = {
            'x-xsrf-token': xsrf.replace('%3D', '='),
            'origin': 'https://www.immoweb.be',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'cookie': f'XSRF-TOKEN={xsrf}; immoweb_session={immoweb_session}',
            'content-type': 'application/json;charset=UTF-8'
        }
        yield scrapy.Request(url=url,
                             method='POST',
                             body=payload,
                             headers=headers,
                             callback=self.extract_pages
                             )


    def extract_pages(self, response):
        print(response.json())
        for i in range(1, 334):
            yield scrapy.Request(
                url=self.page_url.format(i),
                callback=self.extract_ids,
                headers=response.headers
            )



    def extract_ids(self, response):
        try:
            res_data = response.json()
            for ids in res_data['results']:
                id = ids['id']

                yield scrapy.Request(url='https://www.immoweb.be/en/statistics/summary/{}'.format(id),
                                     meta=response.meta,
                                     callback=self.extract_stats,
                                     cb_kwargs={'id': id})
        except:
            self.log('Could not extract ids for  : {}'.format(response.request.url))



    def extract_stats(self, response, id):
        try:
            res_data = response.json()
            print(res_data)
            yield scrapy.Request(url='https://www.immoweb.be/en/classified/{}'.format(id),
                                 meta=response.meta,
                                 callback=self.extract_data,
                                 cb_kwargs={'stats': res_data})
        except:
            self.log('Could not extract stats for id  : {}'.format(id))



    # data extaction code
    def extract_data(self, response, stats):

        data = {}
        tr = response.xpath('//div[@class="text-block__body"]//table[@class="classified-table"]//tr')
        for i in tr:
            key = ' '.join(i.xpath('string(./th)').get(default='').strip().replace('\n', '').lower().split())
            value = ' '.join(i.xpath('string(./td)').get(default='').strip().replace('\n', '').lower().split())
            print(key, value)

            if key:
                data[key] = value

        # overview
        overview = {}
        y = response.xpath('//h2[contains(text(), "Overview")]/following-sibling::div//div[@class="overview__item"]');
        for i in y:
            y1 = i.xpath('string()').get()
            v1 = ' '.join(y1.split())
            if 'bedroom' in v1:
                overview['bedroom'] = v1.split()[0]
            elif 'bathroom' in v1:
                overview['bathroom'] = v1.split()[0]
            elif 'livable space' in v1:
                overview['livable space'] = v1.split()[0]
            elif 'land' in v1:
                overview['land space'] = v1.split()[0]
            elif 'm²' in v1:
                overview['livable space'] = v1.split()[0]
            else:
                if 'unlisted' in overview:
                    overview['unlisted'].append(v1)
                else:
                    overview['unlisted'] = [v1]

        data['overview'] = overview

        # images
        r = response.xpath('//header/following::script[1]').get()
        start = r.index('{"id"')
        end = r.index(';\n\n')
        modified_resp = r[start:end]
        json_resp = json.loads(modified_resp)
        images = json_resp['media']['pictures']
        final_images = [i['largeUrl'] for i in images]

        data['images'] = final_images
        price = json_resp['price']['mainValue']
        if price:
            data['price'] = price


        data['posted_on'] = json_resp['publication']['creationDate'][:10]


        # property details
        property_dict = {
            'prop_type': json_resp['property']['type'],
            'desc_title': json_resp['property']['title'],
            'description': json_resp['property']['description'],
            'alternate_description': json_resp['property']['alternativeDescriptions']["nl"],
            'prop_number': json_resp['property']['location']['number'],
            'prop_street': json_resp['property']['location']['street'],
            'prop_locality': json_resp['property']['location']['locality'],
            'prop_district': json_resp['property']['location']['district'],
            'prop_province': json_resp['property']['location']['province'],
            'prop_postal_code': json_resp['property']['location']['postalCode'],
            'prop_region': json_resp['property']['location']['region'],
            'prop_country': json_resp['property']['location']['country'],
            'floor': json_resp['property']['location']['floor']
        }

        # agency detls
        agency_dict = {
            'agency_email': json_resp['customers'][0]['email'],
            'agency_phone': json_resp['customers'][0]['phoneNumber'],
            'agency_name': json_resp['customers'][0]['name'],
            'agency_website': json_resp['customers'][0]['website'],
            'agency_street': json_resp['customers'][0]['location']['street'],
            'agency_locality': json_resp['customers'][0]['location']['locality'],
            'agency_district': json_resp['customers'][0]['location']['district'],
            'agency_postal_code': json_resp['customers'][0]['location']['postalCode'],
            'agency_province': json_resp['customers'][0]['location']['province'],
            'agency_region': json_resp['customers'][0]['location']['region'],
            'agency_country': json_resp['customers'][0]['location']['country'],
        }

        for i in property_dict:
            if property_dict[i]:
                data[i] = property_dict[i]

        for i in agency_dict:
            if agency_dict[i]:
                data[i] = agency_dict[i]

        for key, value in stats.items():
            data['views'] = value['views']
            data['bookmarks'] = value['bookmarks']


        # for i in final_images:
        #     yield scrapy.Request(url=i,
        #                          cb_kwargs={'data': data}
        #                          )
        yield data


    def process_images(self, response, data):
        pass




if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(ImmowebExtraction)
    process.start()