import json
import re
import scrapy


class ImmomapExtraction(scrapy.Spider):
    name = "immomap_extraction_spider"

    # extract all the ids
    # call on these ids from the data of property
    # extract data points from the property's page

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = "https://www.immomaps.be/en/listings?filter%5Btransaction_type%5D=for_sale&filter%5Bproperty_type%5D=houseapartment&sort=recommended&page="
        self.listing_url = 'https://www.immomaps.be/en/listings/'


    def start_requests(self):

        # for i in range(1,69):
            yield scrapy.Request(
                url=self.url+str(1),
                callback=self.get_pages,
            )

    def get_pages(self, response):
        r = response.xpath('//div[@id="app"]/@data-page').get()
        json_res = json.loads(r)
        markers = json_res['props']['markers']
        ids = []
        for i in markers:
            ids.append(i['uuid'])

        for i in ids:
            yield scrapy.Request(
                url=self.listing_url + i,
                callback=self.extract_data
            )



    def extract_data(self, response):
        res = response.xpath('//div[@id="app"]/@data-page').get()
        json_res = json.loads(res)
        print(json_res)
        dict = json_res['props']['listing']

        # list = ['title', 'main_property_type', 'property_type', 'street', 'number', 'postcode', 'city', 'province',
        #         'provider', 'lat', 'lng', 'price', 'price_per_sqm', 'rental_charges', 'habitable_surface_area',
        #         'total_surface_area', 'bedrooms', 'bathrooms', 'toilets', 'parking_spaces', 'garden',
        #         'garden_surface_area', 'terrace', 'terrace_surface_area', 'swimming_pool',
        #         'to_be_renovated', 'year_built', 'delivery',
        #          'elevator', 'cadastral_income', 'epc_value', 'epc_score', 'epc_certificate_number',
        #         'heating_type', 'heating_type_labels', 'air_conditioning', 'solar_panels',
        #         'electricity_certificate_available', 'availability', 'availability_label', 'urban_planning_permit',
        #         'subpoena', 'preemption', 'subdivision_permit',
        #         'protected_heritage', 'description', 'seo_description', 'status',
        #         'payment_term', 'contact_email', 'contact_phone', 'views', 'human_time', 'approved_at', 'created_at',
        #         'updated_at', 'thumbnail', 'team']

        # keys = ['title', 'main_property_type', 'property_type', 'street', 'number', 'postcode', 'city', 'province',
        #         'provider', 'lat', 'lng', 'price', 'price_per_sqm', 'habitable_surface_area',
        #         'total_surface_area', 'bedrooms', 'bathrooms', 'toilets', 'parking_spaces', 'garden',
        #         'garden_surface_area', 'terrace', 'terrace_surface_area', 'swimming_pool', 'to_be_renovated',
        #         'year_built', 'elevator', 'cadastral_income', 'epc_value', 'epc_score',
        #         'epc_certificate_number', 'heating_type', 'air_conditioning', 'solar_panels',
        #         'electricity_certificate_available', 'availability', 'urban_planning_permit',
        #         'subpoena', 'preemption', 'subdivision_permit', 'protected_heritage',
        #         'status', 'payment_term', 'contact_email', 'contact_phone', 'views', 'human_time', 'approved_at',
        #         'created_at', 'updated_at']

        keys = ['title', 'main_property_type', 'property_type', 'street', 'number', 'postcode', 'city', 'province',
                'provider', 'lat', 'lng', 'price', 'price_per_sqm',  'habitable_surface_area',
                'total_surface_area', 'bedrooms', 'bathrooms', 'toilets', 'parking_spaces', 'garden',
                'garden_surface_area', 'terrace', 'terrace_surface_area', 'garden_orientation', 'swimming_pool',
                'to_be_renovated', 'furnished', 'suitable_for_cohousing', 'year_built', 'delivery', 'building_type',
                'floor', 'elevator', 'cadastral_income', 'epc_value', 'epc_score', 'epc_certificate_number', 'e_level',
                'heating_type', 'heating_type_labels', 'air_conditioning', 'solar_panels',
                'electricity_certificate_available', 'availability', 'availability_label', 'urban_planning_permit',
                'urban_development_destination', 'subpoena', 'preemption', 'subdivision_permit', 'floodplain',
                'protected_heritage', 'status', 'status_label', 'publication_status', 'payment_term', 'contact_email',
                'contact_phone', 'views', 'human_time', 'thumbnail']

        dates = ['approved_at', 'created_at', 'updated_at']

        data = {}

        # images
        pics = []
        for i in dict['media']:
            pics.append(i['url'])

        data['images'] = pics

        # description
        pattern = '<.*?>'
        desc = re.sub(pattern, '', dict['description']).replace('&nbsp;', '').replace('  ', '')
        data['description'] = desc


        for i in keys:
            data[i] = dict[i]

        for i in dates:
            data[i] = dict[i][:10]

        yield data