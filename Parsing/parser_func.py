import requests
from bs4 import BeautifulSoup
from pprint import pprint
from tqdm import tqdm
from db_client import insert_flat

PARAM_PATTERN = {
    'Количество комнат': 'rooms',
    'Площадь общая': 'square',
    'Год постройки': 'year',
    'Этаж / этажность': 'floor',
    'Тип дома': 'type_house',
    'Область': 'region',
    'Населенный пункт': 'city',
    'Улица': 'street',
    'Район города': 'district',
    'Координаты': 'coordinates'
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}
URL = 'https://realt.by/sale/flats/'


def get_last_page() -> int:
    response = requests.get(URL, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    last_page = soup.find_all('a',
                              class_='focus:outline-none sm:focus:shadow-10bottom cursor-pointer select-none inline-flex font-normal text-body min-h-[2.5rem] min-w-[2.5rem] py-0 items-center !px-1.25 justify-center mx-1 hover:bg-basic-200 rounded-md disabled:text-basic-500')
    last_page = last_page[-1].text
    return int(last_page)


def get_all_links(last_page: int) -> list:
    links = []
    for page in tqdm(range(1, last_page + 1), desc='PARSER URLS: '):
        response = requests.get(f'{URL}?page={page}', headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        raw_links = soup.find_all('a', class_='z-1 absolute top-0 left-0 w-full h-full cursor-pointer', href=True)
        urls = [f'https://realt.by{el["href"]}' for el in raw_links]
        links.extend(urls)

    return links


def get_flats_data(links: list) -> dict:
    flats = {}
    for link in tqdm(links, desc='parsing data: '):
        flat = {'rooms': '', 'square': '', 'year': '', 'floor': '', 'type_house': '', 'region': '', 'city': '',
                'street': '', 'district': '', 'coordinates': ''}

        resp = requests.get(link, headers=headers)
        print(resp.status_code)
        flat_id = resp.url.split('/')[-2]
        print(flat_id)
        flat['flat_id'] = flat_id
        s = BeautifulSoup(resp.text, 'lxml')
        title = s.find('h1', {
            "class": "order-1 mb-0.5 md:-order-2 md:mb-4 block w-full !inline-block lg:text-h1Lg text-h1 font-raleway font-bold flex items-center"}).text
        try:
            price = s.find('h2',
                           class_='!inline-block mr-1 lg:text-h2Lg text-h2 font-raleway font-bold flex items-center').text.replace(
                'р.', '').replace(' ', '')

        except Exception as e:
            price = '-1'

        try:
            description = s.find('div', class_=['description_wrapper__tlUQE']).text
        except Exception as e:
            description = ''
        # pprint(description)

        try:
            image = s.find('div', class_='absolute inset-0').find_all('img')[1]['src']
        except Exception as e:
            image = ''
        # print(image)

        raw_params = s.find_all('li', class_="relative py-1")

        for param in raw_params:
            key = param.find('span').text
            if key not in PARAM_PATTERN:
                continue
            value = param.find(['p', 'a']).text.replace('г. ', '').replace(' м²', '')
            flat[PARAM_PATTERN[key]] = value

        flat['title'] = title
        flat['price'] = int(price)
        flat['image'] = image
        flat['description'] = description
        flats[flat_id] = flat
    return flats


def run_parser():
    last_page = get_last_page()
    links = get_all_links(2)
    data = get_flats_data(links)
    for item in data.values():
        insert_flat(item)


run_parser()
