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
    filter_enum_type_of_market = ['secondary', 'primary', 'secondary,primary']
    filter_enum_comission = ['yes', 'no', 'yes,no']
    filter_enum_furnished = ['yes', 'no', 'yes,no']
    currencies = ['UZS', 'UYE']
    repairs = [i for i in range(1, 7)]
    sorts = ['created_at:desc',
             'filter_float_price:desc',
             'relevance:desc',
             'filter_float_price:asc']
    for f_type_of_market in filter_enum_type_of_market:
        params = {'category_id': 13}
        if 'limit' not in params.keys():
            params['limit'] = 50
        if 'offset' not in params.keys():
            params['offset'] = 0
        params['filter_enum_type_of_market'] = f_type_of_market
        for currency in currencies:
            params['currency'] = currency
            for f_furnished in filter_enum_furnished:
                params['filter_enum_furnished'] = f_furnished
                for f_comission in filter_enum_comission:
                    params['filter_enum_comission'] = f_comission
                    for repair in repairs:
                        params['filter_enum_repairs'] = repair
                        for sort in sorts:
                            params['sort_by'] = sort
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


def get_offers(url=None, params=None):
    if params is None:
        params = {}
    session_timeout = aiohttp.ClientTimeout(total=None)
    session = aiohttp.ClientSession(headers=headers, timeout=session_timeout)
    responses = {}
    if url:
        with session.get(url) as resp:
            if resp.status == 200:
                responses = resp.json()
    else:
        with session.get('https://www.olx.uz/api/v1/offers/', params=params) as resp:
            if resp.status == 200:
                r = resp.json(encoding="utf-8")
                response = [r]
                responses = {"responses": response}
    session.close()
    return responses


class UploadOlx(QThread):
    db_res = []
    init_update_db = pyqtSignal()

    def __init__(self, db_res):
        super().__init__()
        self.update_db(db_res)

    def update_db(self, db_res):
        self.db_res = db_res

    def run(self):
        start_main = datetime.now()
        combo = create_param_combos()
        for params in combo:
            start = datetime.now()
            total_elements = []
            try:
                resp = get_offers(params=params)
            except (ClientOSError, ClientPayloadError) as er:
                time.sleep(10)
                print(er)
                continue
            responses = resp.get("responses")
            print(len(responses))
            new_offers = []
            for response in responses:
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
                meta = response.get('metadata')
                total_elements.append(meta.get('visible_total_count'))
                print(responses.index(response), meta.get('visible_total_count'))
                new_offers = [one_offers
                              for one_offers in new_offers
                              if one_offers not in self.db_res]
                try:
                    # todo post to database
                    url = BASE_API + "post_flat"
                    flats_to_post_dict = [flat.__dict__
                                          for flat in new_offers
                                          if flat not in self.db_res]
                    print(len(flats_to_post_dict))
                    post_r = requests.post(url=url, json=flats_to_post_dict)
                    print(post_r)
                    delay = random.randint(0, 10)
                    print("Delay: ", delay)
                    time.sleep(delay)
                    self.init_update_db.emit()
                except Exception as err:
                    print(err)
                    time.sleep(1)
                    continue
                next_page = resp.get('links', {}).get('next', {}).get('href')
                while next_page:
                    try:
                        resp1 = get_offers(next_page)
                    except ClientOSError as er:
                        time.sleep(10)
                        print(er)
                        break
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
                            url=f'https://www.olx.uz/api/v1/offers/{one.get("id")}',
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
                                  if one_offers not in self.db_res]
                    next_page = resp1.get('links', {}).get('next', {}).get('href')
                    try:
                        # todo post to database
                        url = BASE_API + "post_flat"
                        flats_to_post_dict = [flat.__dict__
                                              for flat in new_offers
                                              if flat not in self.db_res]
                        print(len(flats_to_post_dict))
                        post_r = requests.post(url=url, json=flats_to_post_dict)
                        delay = random.randint(0, 10)
                        print("Delay: ", delay)
                        time.sleep(delay)
                        self.init_update_db.emit()
                        print(post_r)
                    except Exception as err:
                        print(err)
                        time.sleep(1)
                        continue
            print()
            print('Cycle duration: ', f'{(datetime.now() - start).total_seconds() :.3f}s', )
            print('Time from start: ', f'{(datetime.now() - start_main).total_seconds() :.3f}s',
                  f'{len(self.db_res)}/ {total_elements}')

