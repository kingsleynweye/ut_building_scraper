import os
from bs4 import BeautifulSoup
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class Scrape:
    __FACILITIES_URL = 'https://utdirect.utexas.edu/apps/campus/buildings/nlogon/facilities'
    __PROVOST_URL = 'https://raw.githubusercontent.com/kingsleynweye/ut_building_scraper/master/data/building_metadata_provost.xlsx'

    @staticmethod
    def facilities(building_abbreviations=None):
        sites =  pd.DataFrame(Scrape.get_sites()).explode(column='building_abbreviation',ignore_index=True)

        if building_abbreviations:
            sites = sites[sites['building_abbreviation'].isin(building_abbreviations)].copy()
        else:
            pass

        data = []
        session = Scrape.__get_session()
        response = session.get(Scrape.__FACILITIES_URL)
        soup = BeautifulSoup(response.text.encode('UTF-8'),'html.parser')
        sites = sites.to_dict(orient='records')

        for i, record in enumerate(sites):
            site_url = os.path.join(Scrape.__FACILITIES_URL,record['site_abbreviation'])
            building_data = {}
            building_url = os.path.join(site_url,record['building_abbreviation'])
            response = session.get(building_url)
            soup = BeautifulSoup(response.text.encode('UTF-8'),'html.parser')
            building_data['site_name'] = record['site_name']
            building_data['site_abbreviation'] = record['site_abbreviation']
            building_data['building_name'] = ''.join(soup.find('h2').text.split('(')[0:-1]).strip()
            building_data['building_abbreviation'] = record['building_abbreviation']
            building_data['building_number'] = str(soup.find('h2').text.split('-')[-1].replace(')','').strip())
            building_data['address'] = soup.find('h3').text
            building_info = soup.find('div',{'id':'collapse1'})
            info_keys = building_info.findAll('th')
            info_keys = [key.text for key in info_keys]
            info_values = building_info.findAll('td')
            info_values = [key.text for key in info_values]
            building_data['floors'] = info_values[info_keys.index('Floors:')]
            building_data['gross_square_feet'] = info_values[info_keys.index('Gross Sq. Feet:')].replace(',','')
            building_data['occupied_since'] = info_values[info_keys.index('UT Building Since:')]
            images = soup.find('div',{'class':'carousel-inner'})
            
            if images:
                building_data['building_image_urls'] = ';'.join([f'https://utdirect.utexas.edu{image["src"]}' for image in images.findAll('img')])
            else:
                pass

            data.append(building_data)

        if len(data) > 0:
            data = pd.DataFrame(data)
            data = data.replace('None',None)
            str_columns = ['site_name','site_abbreviation','building_name','building_abbreviation','building_number','address','building_image_urls']
            int_columns = ['floors','occupied_since']
            flt_columns = ['gross_square_feet']
            data[str_columns] = data[str_columns].astype(str,errors='ignore')
            data[int_columns] = data[int_columns].astype(float,errors='ignore').astype(int,errors='ignore')
            data[flt_columns] = data[flt_columns].astype(float,errors='ignore')
        else:
            data = None

        return data

    @staticmethod
    def provost():
        data = pd.read_excel(Scrape.__PROVOST_URL,skiprows=4)
        # data.columns = [column.lower().replace(' ','_') for column in data.columns]
        # data = data.rename(columns={
        #     'initial_occupancy_year':'initial_occupancy_year',
        #     'ut_occupancy_date':'ut_occupancy_year',
        #     'number_of_floors':'floors',
        #     'gross_area_(gsf)':'gross_area',
        #     'net_usable_area_(assignable_+_non-assignable)':'net_usable_area',
        #     'non-assignable_area':'non_assignable_area',
        #     'e&g_area':'e_and_g_area'
        # })
        # column_map = {
        #     'Site Description':'site',
        #     'Controlling Institution':'controlling_institution',
        #     'Building Number':'building_number',
        #     'Building Abbreviation':'building_abbreviation',
        #     'Building Name':'building_name',
        #     'Address':'address',
        #     'City':'city',
        #     'State':'state',
        #     'ZIP':'zip_code',
        #     'Status':'status'
        # }
        return data

    @staticmethod
    def __get_session():
        session = requests.Session()
        retries = Retry(total=5,backoff_factor=1,status_forcelist=[502,503,504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        return session

    @staticmethod
    def get_sites():
        session = Scrape.__get_session()
        response = session.get(Scrape.__FACILITIES_URL)
        soup = BeautifulSoup(response.text.encode('UTF-8'),'html.parser')
        sites = soup.find('select',{'id':'js-site'}).findAll('option')
        data = []

        for site in sites[1:]:
            site_abbreviation = site.get('value')
            site_name = site.text
            site_url = os.path.join(Scrape.__FACILITIES_URL,site_abbreviation)
            response = session.get(site_url)
            soup = BeautifulSoup(response.text.encode('UTF-8'),'html.parser')
            hrefs = soup.find('table',{'id':'myTable'}).find('tbody').findAll('a')
            building_abbreviations = [href.text for href in hrefs]
            data.append({
                'site_abbreviation':site_abbreviation,
                'site_name':site_name,
                'building_abbreviation':building_abbreviations
            })
        
        return data