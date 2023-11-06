import time
import aiohttp

import requests
from PyQt6.QtCore import QThread
from flat import Flat, REPAIR_CHOICES_UYBOR, BASE_API, headers


def get_olx(id):
    url = f"https://www.olx.uz/api/v1/offers/{id}"
    session_timeout = aiohttp.ClientTimeout(total=None)
    session = aiohttp.ClientSession(headers=headers, timeout=session_timeout)
    request = session.get(url)
    return request


def get_uybor(id):
    url = f"https://api.uybor.uz/api/v1/listings/{id}"
    request = requests.get(url).json()
    return request


class Checker(QThread):
    db_res = []

    def __init__(self, db_res):
        super().__init__()
        self.update_db(db_res)

    def update_db(self, db_res):
        self.db_res = db_res

    def run(self):

        for one in self.db_res:
            if one.domain == "uybor":
                req = get_uybor(one.external_id)
                print(req, )
                continue
                if req.get('updatedAt') != one.modified:
                    address = ''
                    if req['zone'] is not None:
                        address += req['zone']['name']['ru']
                    if req['region'] is not None:
                        address += ' ' + req['region']['name']['ru']
                    if req['cityId'] is not None:
                        address += ' ' + req['city']['name']['ru']
                    if req['district'] is not None:
                        address += ' ' + req['district']['name']['ru']
                    if req['metro'] is not None:
                        address += ' ' + req['metro']['name']['ru']
                    if req['residentialComplex'] is not None:
                        address += ' ' + req['residentialComplex']['name']['ru']
                    if req['address'] is not None:
                        address += ' ' + req['address']
                    if req['repair'] is not None:
                        repair = REPAIR_CHOICES_UYBOR[req['repair']]
                    else:
                        repair = REPAIR_CHOICES_UYBOR['repair']
                    if req['isNewBuilding']:
                        is_new_building = 'Новостройки'
                    else:
                        is_new_building = 'Вторичный'
                    if not isinstance(req['room'], int):
                        room = req['room']
                    else:
                        if req['room'] == 'freeLayout':
                            room = 'Студия'
                        else:
                            room = ''
                    flat = Flat(
                        url=f'https://uybor.uz/listings/{req["id"]}',
                        square=float(req['square']),
                        floor=f'{req["floor"]}',
                        total_floor=f'{req["floorTotal"]}',
                        address=address,
                        repair=repair,
                        is_new_building=is_new_building,
                        room=room,
                        modified=req['updatedAt'],
                        price_uye=req['prices']['usd'],
                        price_uzs=req['prices']['uzs'],
                        description=req['description'],
                        id=req['id'],
                        domain="uybor"
                    )
            else:
                req = get_olx(one.external_id)
                if req.get('last_refresh_time') != one.modified:
                    params_get = req.get('params')
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
                    location = req.get('location')
                    address = ''
                    if "city" in location:
                        address += location.get("city").get("name")
                    if "district" in location:
                        address += location.get("district").get("name")
                    if "region" in location:
                        address += location.get("region").get("name")
                    flat = Flat(
                        id=req.get('id'),
                        url=req.get('url'),
                        # url=f'https://www.olx.uz/api/v1/offers/{one.get("id")}',
                        square=float(total_area),
                        description=req.get('description') + req.get('title'),
                        modified=req.get('last_refresh_time'),
                        floor=floor,
                        total_floor=total_floors,
                        room=number_of_rooms,
                        is_new_building=type_of_market,
                        price_uye=price_uye,
                        price_uzs=price_uzs,
                        address=address,
                        repair=repair,
                        domain="olx")
                url = BASE_API + "post_flats"
                flat_dict = [flat.prepare_to_dict()]
                try:
                    post_r = requests.post(url=url, json=flat_dict)
                # print(post_r)
                    print(post_r)
                    #todo emit to update
                except Exception as err:
                    print(err, "blyadina on checker")
                    time.sleep(10)
                    continue

