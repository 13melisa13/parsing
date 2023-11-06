import asyncio
import random
import time
import aiohttp
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from aiohttp.client_exceptions import ClientOSError, ClientPayloadError
from datetime import datetime

from flat import Flat, BASE_API, headers


def create_param_combos():
    list_combo_params = []
    sorts = ['created_at:desc',
             'filter_float_price:desc',
             'relevance:desc',
             'filter_float_price:asc']
    for _ in range(100):
        for sort in sorts:
            params = {'category_id': 13}
            if 'limit' not in params.keys():
                params['limit'] = 50
            if 'offset' not in params.keys():
                params['offset'] = 0
            params['sort_by'] = sort
            if 'currency' not in params.keys():
                params['currency'] = random.choice(['UZS', 'UYE'])
            if 'filter_enum_type_of_market' not in params.keys():
                params['filter_enum_type_of_market'] = random.choice(
                    ['secondary', 'primary', 'secondary,primary'])
            if 'filter_enum_comission' not in params.keys():
                params['filter_enum_comission'] = random.choice(['yes', 'no', 'yes,no'])
            if 'filter_enum_furnished' not in params.keys():
                params['filter_enum_furnished'] = random.choice(['yes', 'no', 'yes,no'])
            if random.choice([True, False, False]) and 'filter_enum_repairs' not in params.keys():
                params['filter_enum_repairs'] = random.randint(1, 6)
            if random.choice([True, False, False]) and 'filter_float_floor:from' not in params.keys():
                params['filter_float_floor:from'] = float(random.randint(1, 20))
            if random.choice([True, False, False]) and 'filter_float_floor:to' not in params.keys():
                params['filter_float_floor:to'] = float(random.randint(1, 100))
            if random.choice(
                    [True, False, False]) and 'filter_float_total_area:from' not in params.keys():
                params['filter_float_total_area:from'] = float(random.randint(1, 100))
            elif random.choice(
                    [True, False, False]) and 'filter_float_total_area:to' not in params.keys():
                params['filter_float_total_area:to'] = float(random.randint(1, 10000))
            if random.choice([True, False, False]) and 'filter_float_price:from' not in params.keys():
                params['filter_float_price:from'] = random.randint(0, 10000000)
            elif random.choice([True, False, False]) and 'filter_float_price:to' not in params.keys():
                params['filter_float_price:to'] = random.randint(0, 10000000)
            if random.choice(
                    [True, False, False]) and 'filter_float_number_of_rooms:from' not in params.keys():
                params['filter_float_number_of_rooms:from'] = float(random.randint(1, 6))
            elif random.choice(
                    [True, False, False]) and 'filter_float_number_of_rooms:to' not in params.keys():
                params['filter_float_number_of_rooms:to'] = float(random.randint(1, 10))
            list_combo_params.append(params)
    return list_combo_params


async def get_offers(url=None, params=None):
    if params is None:
        params = {}
    session_timeout = aiohttp.ClientTimeout(total=None)
    session = aiohttp.ClientSession(headers=headers, timeout=session_timeout)

    if url:
        async with session.get(url) as resp:
            if resp.status == 200:
                response = await resp.json()
    else:
        async with session.get('https://www.olx.uz/api/v1/offers/', params=params) as resp:
            if resp.status == 200:
                response = await resp.json()

    await session.close()
    return response


class UploadOlx(QThread):
    db_res = []
    init_update_db = pyqtSignal()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_olx_polling())
        loop.close()

    def __init__(self, db_res):
        super().__init__()
        self.update_db(db_res)

    def update_db(self, db_res):
        self.db_res = db_res

    async def start_olx_polling(self):
        total_elements = []
        while True:
            print("upload olx start")
            db_res = self.db_res
            start_main = datetime.now()
            combo = create_param_combos()
            print(len(combo), )
            # for params in combo:
            params = random.choice(combo)
            print(combo.index(params), "parMA", params.keys)
            start = datetime.now()

            new_offers = []
            while True:
                try:
                    resp = await get_offers(params=params)
                    # print(resp)
                    break
                except (ClientOSError, ClientPayloadError) as er:
                    await asyncio.sleep(10)
                    print(er)
                    continue
            response = resp
            meta = response.get('metadata')
            total_elements.append(meta.get('visible_total_count'))
            total_floors = 0
            total_area = 0
            floor = 0
            number_of_rooms = ''
            type_of_market = ''
            price_uye = 0
            price_uzs = 0
            repair = ''
            # print(response.get('data'))
            for one in response.get('data'):
                params_get = one.get('params')
                for param in params_get:
                    key = param.get("key")
                    if key == 'total_floors':
                        total_floors = param.get('value').get('key')
                    elif key == 'total_area':
                        total_area = param.get('value').get('key')

                    elif key == 'floor':
                        floor = param.get('value').get('key')
                    elif key == 'number_of_rooms':
                        number_of_rooms = param.get('value').get('key')
                    elif key == 'type_of_market':
                        if param.get('value').get('key') == 'Вторичный рынок':
                            type_of_market = "Вторичный"
                        else:
                            type_of_market = "Новостройка"
                    elif key == 'price':
                        # print(param)
                        price_uzs = param.get('value').get('converted_value')
                        price_uye = param.get('value').get('value')
                    elif key == 'repairs':
                        repair = param.get('value').get('label')
                location = one.get('location')
                address = ''
                if "city" in location:
                    address += location.get("city").get("name")
                if "district" in location:
                    address += location.get("district").get("name")
                if "region" in location:
                    address += location.get("region").get("name")
                # print(price_uzs, "БЛЯДСКИЙ НАХУЙ ПРАЙС УБЕКОВСКИЙ")
                flat = Flat(
                    id=one.get('id'),
                    url=one.get('url'),
                    # url=f'https://www.olx.uz/api/v1/offers/{one.get("id")}',
                    square=float(total_area),
                    description=one.get('description') + one.get('title'),
                    modified=one.get('last_refresh_time'),
                    floor=floor,
                    total_floor=total_floors,
                    room=number_of_rooms,
                    is_new_building=type_of_market,
                    price_uye=price_uye,
                    price_uzs=price_uzs,
                    address=address,
                    repair=repair,
                    domain="olx")
                new_offers.append(flat)
                # print(new_offers)

                # print(responses.index(response), meta.get('visible_total_count'))
            new_offers = [one_offers
                          for one_offers in new_offers
                          if one_offers not in db_res
                          or one_offers.modified != db_res[db_res.index(one_offers)].modified]

            while True:
                try:
                    url = BASE_API + "post_flats"
                    flats_to_post_dict = [flat.prepare_to_dict()
                                          for flat in new_offers
                                        if flat not in db_res
                                          or flat.modified != db_res[db_res.index(flat)].modified]

                    # print(flats_to_post_dict[0])
                    post_r = requests.post(url=url, json=flats_to_post_dict, headers=headers)
                    print(post_r.status_code, "olx upload", len(flats_to_post_dict), len(new_offers))
                    delay = random.randint(0, 10)
                    print("Delay: ", delay)
                    await asyncio.sleep(delay)
                    self.init_update_db.emit()
                    if post_r.status_code != 200:
                        time.sleep(10)
                        print(post_r.status_code)
                        continue
                    flats_to_post = []
                    break
                except Exception as err:
                    print(err)
                    await asyncio.sleep(1)
                    continue

            next_page = resp.get('links', {}).get('next', {}).get('href')
            while next_page:
                try:
                    resp1 = await get_offers(next_page)
                    response1 = resp1
                except ClientOSError as er:
                    await asyncio.sleep(10)
                    print(er)
                    break
                for one in response1.get('data'):
                    total_floors = ''
                    total_area = ''
                    floor = ''
                    number_of_rooms = ''
                    type_of_market = ''
                    price_uye = ''
                    price_uzs = ''
                    repair = ''
                    params_get = one.get('params')
                    for param in params_get:
                        key = param.get("key")
                        if key == 'total_floors':
                            total_floors = param.get('value').get('key')
                        elif key == 'total_area':
                            total_area = param.get('value').get('key')
                        elif key == 'floor':
                            floor = param.get('value').get('key')
                        elif key == 'number_of_rooms':
                            number_of_rooms = param.get('value').get('key')
                        elif key == 'type_of_market':
                            if param.get('value').get('key') == 'Вторичный рынок':
                                type_of_market = "Вторичный"
                            else:
                                type_of_market = "Новостройка"
                        elif key == 'price':
                            price_uzs = param.get('value').get('converted_value')
                            price_uye = param.get('value').get('value')
                        elif key == 'repairs':
                            repair = param.get('value').get('label')
                    location = one.get('location')
                    address = ''
                    if "city" in location:
                        address += location.get("city").get("name")
                    if "district" in location:
                        address += location.get("district").get("name")
                    if "region" in location:
                        address += location.get("region").get("name")
                    flat = Flat(
                        id=one.get('id'),
                        url=one.get('url'),
                        square=float(total_area),
                        description=one.get('description') + one.get('title'),
                        modified=one.get('last_refresh_time'),
                        floor=floor,
                        total_floor=total_floors,
                        room=number_of_rooms,
                        is_new_building=type_of_market,
                        price_uye=price_uye,
                        price_uzs=price_uzs,
                        address=address,
                        repair=repair,
                        domain="olx")
                    new_offers.append(flat)
                new_offers = [one_offers
                              for one_offers in new_offers
                              if one_offers not in db_res]
                next_page = resp1.get('links', {}).get('next', {}).get('href')
                try:
                    # todo post to database
                    url = BASE_API + "post_flats"
                    flats_to_post_dict = [flat.prepare_to_dict()
                                          for flat in new_offers
                                          if flat not in db_res
                                          or flat.modified != db_res[db_res.index(flat)].modified]
                    # print(len(flats_to_post_dict))
                    post_r = requests.post(url=url, json=flats_to_post_dict, headers=headers)
                    print(post_r.status_code, "olx upload", len(flats_to_post_dict), len(new_offers))
                    delay = random.randint(0, 10)
                    print("Delay: ", delay)
                    await asyncio.sleep(delay)
                    self.init_update_db.emit()
                    print(post_r.status_code)
                except Exception as err:
                    print(err)
                    await asyncio.sleep(1)
                    continue
            print()
            print('Cycle duration: ', f'{(datetime.now() - start).total_seconds() :.3f}s', )
            print('Time from start: ', f'{(datetime.now() - start_main).total_seconds() :.3f}s',
                  f'{len(db_res)}/ {total_elements}')
