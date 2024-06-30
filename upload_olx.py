import asyncio
import random
import aiohttp
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from aiohttp.client_exceptions import ClientOSError, ClientPayloadError
from datetime import datetime

from models.commerce import Commerce
from models.flat import Flat
from config import BASE_API, headers
from models.land import Land


def create_param_combos(type_of_real_estate):
    list_combo_params = []
    sorts = ['created_at:desc',
             'filter_float_price:desc',
             'relevance:desc',
             'filter_float_price:asc']

    for _ in range(100):
        for sort in sorts:
            params = {}
            match type_of_real_estate:

                case 'flat':
                    params = {'category_id': random.choice([13, 1566, 1147])}
                    if random.choice([False, False, False, True]):
                        if 'filter_enum_type_of_market' not in params.keys():
                            params['filter_enum_type_of_market'] = random.choice(
                                ['secondary', 'primary', 'secondary,primary'])

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
                        if random.choice(
                                [True, False, False]) and 'filter_float_number_of_rooms:from' not in params.keys():
                            params['filter_float_number_of_rooms:from'] = float(random.randint(1, 6))
                        elif random.choice(
                                [True, False, False]) and 'filter_float_number_of_rooms:to' not in params.keys():
                            params['filter_float_number_of_rooms:to'] = float(random.randint(1, 10))
                case 'commerce':
                    params = {'category_id': random.choice([14, 11])}
                    if random.choice([False, False, False, True]):
                        if random.choice(
                                [True, False, False]) and 'filter_float_total_area:from' not in params.keys():
                            params['filter_float_total_area:from'] = float(random.randint(1, 180))
                        elif random.choice(
                                [True, False, False]) and 'filter_float_total_area:to' not in params.keys():
                            params['filter_float_total_area:to'] = float(random.randint(1, 180))
                        if random.choice([True, False, False]) and 'filter_enum_premise_type' not in params.keys():
                            params['filter_enum_premise_type'] = random.randint(1, 12)
                case 'land':
                    params = {'category_id': random.choice([10, 1533])}
                    if random.choice([False, False, False, True]):
                        if random.choice([True, False, False]) and 'filter_enum_location' not in params.keys():
                            params['filter_enum_location'] = random.randint(1, 8)
                        if random.choice([True, False, False]) and 'filter_enum_purpose' not in params.keys():
                            params['filter_enum_purpose'] = random.randint(1, 5)
                        if random.choice(
                                [True, False, False]) and 'filter_float_land_area:from' not in params.keys():
                            params['filter_float_land_area:from'] = float(random.randint(1, 1000))
                        elif random.choice(
                                [True, False, False]) and 'filter_float_land_area:to' not in params.keys():
                            params['filter_float_land_area:to'] = float(random.randint(1, 1001))
                        if 'currency' not in params.keys():
                            params['currency'] = random.choice(['UZS', 'UYE'])
                        if random.choice([True, False, False]) and 'filter_float_price:from' not in params.keys():
                            params['filter_float_price:from'] = random.randint(0, 10000000)
                        elif random.choice([True, False, False]) and 'filter_float_price:to' not in params.keys():
                            params['filter_float_price:to'] = random.randint(0, 10000000)
                        if 'filter_enum_comission' not in params.keys():
                            params['filter_enum_comission'] = random.choice(['yes', 'no', 'yes,no'])
            if 'limit' not in params.keys():
                params['limit'] = 1
            if 'offset' not in params.keys():
                params['offset'] = 0
            params['sort_by'] = sort

            list_combo_params.append(params)
    return list_combo_params


async def get_offers(url=None, params=None):
    if params is None:
        params = {}
    session_timeout = aiohttp.ClientTimeout(total=None)
    session = aiohttp.ClientSession(headers=headers, timeout=session_timeout)
    response = None
    if url and session:
        async with session.get(url) as resp:
            if resp.status == 200:
                response = await resp.json()
    else:
        if session:
            async with session.get('https://www.olx.uz/api/v1/offers/', params=params) as resp:
                if resp.status == 200:
                    response = await resp.json()

    await session.close()
    return response


def cat_definer(cat_id):
    print("Upload olx cat id ", cat_id)
    match cat_id:
        case 13:
            return 'sale'
        case 1513:
            return 'exchange'
        case 14:
            return 'sale'
        case 11:
            return 'rent'
        case 10:
            return 'sale'
        case 1147:
            return 'long_term_rent'
        case 1533:
            return 'rent'
        case 1566:
            return 'short_term_rent'
        case _:
            return 'sale'


def response_page_to_list_flat(response, total_elements, new_offers, type_real_estate):
    if not response:
        return []
    meta = response.get('metadata')
    if not meta or not response.get('data'):
        return []
    total_elements.append(meta.get('visible_total_count'))

    match type_real_estate:
        case 'flat':
            for one in response.get('data'):
                total_floors = ''
                total_area = 1
                floor = ''
                number_of_rooms = ''
                type_of_market = ''
                price_uye = 0
                price_uzs = 0
                repair = ''
                params_get = one.get('params')
                if 'category' in one.keys():
                    category_id = one.get('category').get('id')
                else:
                    category_id = 13

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
                        if param.get('value').get('key') == 'secondary':
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

                flat = Flat(
                    id=one.get('id'),
                    url=one.get('url'),
                    # url=f'https://www.olx.uz/api/v1/offers/{one.get("id")}',
                    square=float(total_area),
                    description=one.get('description') + one.get('title'),
                    modified=one.get('last_refresh_time'),
                    floor=floor.__str__(),
                    total_floor=total_floors.__str__(),
                    room=number_of_rooms,
                    is_new_building=type_of_market,
                    price_uye=price_uye,
                    price_uzs=price_uzs,
                    address=address,
                    repair=repair,
                    domain="olx",
                    category=cat_definer(category_id)
                )
                new_offers.append(flat)
            return new_offers
        case 'land':
            for one in response.get('data'):
                land_area = 0
                location_feature = ''
                price_uye = 0
                price_uzs = 0
                purpose = ''
                params_get = one.get('params')
                if 'category' in one.keys():
                    category_id = one.get('category').get('id')
                else:
                    category_id = 10
                for param in params_get:
                    key = param.get("key")
                    if key == 'land_area':
                        land_area = param.get('value').get('key')
                    elif key == 'purpose':
                        purpose = param.get('value').get('label')
                    elif key == 'location':
                        location_feature = param.get('value').get('label')
                    elif key == 'price':
                        # print(param)
                        price_uzs = param.get('value').get('converted_value')
                        price_uye = param.get('value').get('value')
                location = one.get('location')
                address = ''
                if "city" in location:
                    address += location.get("city").get("name")
                if "district" in location:
                    address += location.get("district").get("name")
                if "region" in location:
                    address += location.get("region").get("name")

                land = Land(
                    id=one.get('id'),
                    url=one.get('url'),
                    category=cat_definer(category_id),
                    # url=f'https://www.olx.uz/api/v1/offers/{one.get("id")}',
                    square=float(land_area),
                    description=one.get('description') + one.get('title'),
                    modified=one.get('last_refresh_time'),
                    type_of_land=purpose,
                    location_feature=location_feature,
                    price_uye=price_uye,
                    price_uzs=price_uzs,
                    address=address,
                    domain="olx")
                new_offers.append(land)
            return new_offers

        case 'commerce':
            for one in response.get('data'):
                if 'category' in one.keys():
                    category_id = one.get('category').get('id')
                else:
                    category_id = 14
                total_area = 0
                price_uye = 0
                price_uzs = 0
                premise_type = ''
                params_get = one.get('params')
                for param in params_get:
                    key = param.get("key")
                    if key == 'total_area':
                        total_area = param.get('value').get('key')
                    elif key == 'premise_type':
                        premise_type = param.get('value').get('label')
                    elif key == 'price':
                        # print(param)
                        price_uzs = param.get('value').get('converted_value')
                        price_uye = param.get('value').get('value')
                location = one.get('location')
                address = ''
                if "city" in location:
                    address += location.get("city").get("name")
                if "district" in location:
                    address += location.get("district").get("name")
                if "region" in location:
                    address += location.get("region").get("name")

                commerce = Commerce(
                    id=one.get('id'),
                    url=one.get('url'),
                    category=cat_definer(category_id),
                    # url=f'https://www.olx.uz/api/v1/offers/{one.get("id")}',
                    square=float(total_area),
                    description=one.get('description') + one.get('title'),
                    modified=one.get('last_refresh_time'),
                    type_of_commerce=premise_type,
                    price_uye=price_uye,
                    price_uzs=price_uzs,
                    address=address,
                    domain="olx")

                new_offers.append(commerce)
            return new_offers
        case _:
            return None


class UploadOlx(QThread):
    db_res = []
    init_update_db = pyqtSignal()

    def run(self):
        while True:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.start_olx_polling())
                loop.close()
                break
            except Exception as e:
                print("Upload olx ERR", self.type_of_real_estate, e)
                continue

    def __init__(self, db_res, type_of_real_estate):
        super().__init__()
        self.enable_to_post = True
        self.update_db(db_res)
        self.type_of_real_estate = type_of_real_estate

    def switch_url_post(self):
        match self.type_of_real_estate:
            case 'flat':
                return 'post_flats'
            case 'commerce':
                return 'post_commerces'
            case 'land':
                return 'post_lands'

    def update_db(self, db_res):
        self.db_res = db_res

    async def start_olx_polling(self):
        total_elements = []
        while True:
            print(f"start upload {self.switch_url_post()} {datetime.now()}")
            db_res = self.db_res
            start_main = datetime.now()
            combo = create_param_combos(self.type_of_real_estate)
            params = random.choice(combo)
            print("upload olx start", combo.index(params), "parameters", len(combo), params)
            start = datetime.now()
            new_offers = []
            next_page = None
            while True:
                try:
                    resp = await get_offers(params=params)
                except (ClientOSError, ClientPayloadError) as er:
                    await asyncio.sleep(1)
                    print("olx", len(combo), er)
                    resp = []
                    continue
                new_offers = response_page_to_list_flat(resp, total_elements, new_offers, self.type_of_real_estate)
                break
            while True:
                try:
                    url = BASE_API + self.switch_url_post()
                    next_page = None
                    if len(new_offers) == 0:
                        break
                    flats_to_post_dict = [flat.prepare_to_dict()
                                          for flat in new_offers
                                          if flat not in db_res
                                          or flat.modified != db_res[db_res.index(flat)].modified]

                    # print(len(flats_to_post_dict))
                    delay = random.randint(1, 1)
                    # print("Delay: ", delay)
                    await asyncio.sleep(delay)
                    # print(len(flats_to_post_dict))
                    post_r = requests.post(url=url, json=flats_to_post_dict, headers=headers)
                    # print(post_r.status_code, "olx upload", len(flats_to_post_dict), len(new_offers),
                    #       self.type_of_real_estate)
                    self.init_update_db.emit()
                    if 'links' in resp.keys() and 'next' in resp.get('links') and 'href' in resp.get('links').get(
                            'next'):
                        next_page = resp.get('links', {}).get('next', {}).get('href')
                    break
                    # print()
                    if post_r.status_code != 200:
                        await asyncio.sleep(1)
                        print(post_r.status_code)
                        continue
                except Exception as err:
                    print("upload_err_olx1", err)
                    await asyncio.sleep(1)
                    continue


            while next_page:
                try:
                    resp1 = await get_offers(next_page)

                except ClientOSError as er:
                    await asyncio.sleep(1)
                    print("upload_err_olx2", er)

                    break
                new_offers = response_page_to_list_flat(resp1, total_elements, new_offers, self.type_of_real_estate)

                new_offers = [one_offers
                              for one_offers in new_offers
                              if one_offers not in db_res]
                if 'links' in resp1.keys() and 'next' in resp1.get('links') and 'href' in resp1.get('links').get(
                        'next'):
                    next_page = resp1.get('links', {}).get('next', {}).get('href')
                else:
                    break
                try:
                    # #
                    # if not self.enable_to_post:
                    #     await asyncio.sleep(10)
                    #     print("Sleeep on 10 in upload olx")
                    #     continue
                    url = BASE_API + self.switch_url_post()
                    flats_to_post_dict = [flat.prepare_to_dict()
                                          for flat in new_offers
                                          if flat not in db_res
                                          or flat.modified != db_res[db_res.index(flat)].modified]
                    # print(len(flats_to_post_dict))
                    delay = random.randint(5, 15)
                    # print("Delay: ", delay)
                    # print(len(flats_to_post_dict))
                    await asyncio.sleep(delay)
                    post_r = requests.post(url=url, json=flats_to_post_dict, headers=headers)
                    # print(post_r.status_code, "olx upload", len(flats_to_post_dict), len(new_offers), self.type_of_real_estate)
                    self.init_update_db.emit()
                    # print()
                except Exception as err:
                    print("upload_err_olx", err)
                    await asyncio.sleep(1)
                    continue
            # print()
            print(f'Cycle duration {self.type_of_real_estate}: {(datetime.now() - start).total_seconds() :.3f}s', )
            print('Time from start: ', f'{(datetime.now() - start_main).total_seconds() :.3f}s',
                  f'{len(db_res)}/ {total_elements}')
