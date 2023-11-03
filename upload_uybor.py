import math
import time
import requests
from PyQt6.QtCore import QThread

from flat import Flat, REPAIR_CHOICES_UYBOR


def json_uybor(page=0, limit=100):
    url = "https://api.uybor.uz/api/v1/listings"
    params = {
        "limit": limit,
        "page": page,
        "mode": "search",
        "order": "-createdAt",
        "embed": "category,residentialComplex,region,city,district,zone,street,metro",
        "operationType__eq": "sale",
        "category__eq": "7"
    }
    request = requests.get(url, params).json()
    return request["results"], request["total"]


class UploadUybor(QThread):
    db_res = []

    def __init__(self, db_res):
        super().__init__()
        self.update_db(db_res)

    def update_db(self, db_res):
        self.db_res = db_res

    def run(self):
        page = 0
        prev_res = 0
        total = 1
        limit = 100
        while prev_res < total:
            try:
                if limit > (total - prev_res):
                    limit = total - prev_res
                results, total = json_uybor(page, limit)
                flats_to_post = []
            except Exception as err:
                print(err)
                time.sleep(1)
                continue
            for i in range(len(results)):
                address = ''
                if results[i]['zone'] is not None:
                    address += results[i]['zone']['name']['ru']
                if results[i]['region'] is not None:
                    address += ' ' + results[i]['region']['name']['ru']
                if results[i]['cityId'] is not None:
                    address += ' ' + results[i]['city']['name']['ru']
                if results[i]['district'] is not None:
                    address += ' ' + results[i]['district']['name']['ru']
                if results[i]['metro'] is not None:
                    address += ' ' + results[i]['metro']['name']['ru']
                if results[i]['residentialComplex'] is not None:
                    address += ' ' + results[i]['residentialComplex']['name']['ru']
                if results[i]['address'] is not None:
                    address += ' ' + results[i]['address']
                if results[i]['repair'] is not None:
                    repair = REPAIR_CHOICES_UYBOR[results[i]['repair']]
                else:
                    repair = REPAIR_CHOICES_UYBOR['repair']
                if results[i]['isNewBuilding']:
                    is_new_building = 'Новостройки'
                else:
                    is_new_building = 'Вторичный'
                if not isinstance(results[i]['room'], int):
                    room = results[i]['room']
                else:
                    if results[i]['room'] == 'freeLayout':
                        room = 'Студия'
                    else:
                        room = ''
                flats_to_post.append(Flat(
                    url=f'https://uybor.uz/listings/{results[i]["id"]}',
                    square=int(results[i]['square']),
                    floor=f'{results[i]["floor"]}',
                    total_floor=f'{results[i]["floorTotal"]}',
                    address=address,
                    repair=repair,
                    is_new_building=is_new_building,
                    room=room,
                    modified=results[i]['updatedAt'],
                    price_uye=results[i]['prices']['usd'],
                    price_uzs=results[i]['prices']['uzs'],
                    description=results[i]['description'],
                    id=results[i]['id'],
                    domain="uybor"
                ))
            prev_res += len(results)
            try:
                # todo post to database
                ip = ''
                url = f"http://{ip}/get_flats"
                flats_to_post_dict = [flat.__dict__
                                      for flat in flats_to_post
                                      if flat not in self.db_res]
                print(flats_to_post_dict)
                time.sleep(1000)
                requests.post(url=url, json=flats_to_post_dict)
            except Exception as err:
                print(err)
                time.sleep(1)
                continue
            page += 1
