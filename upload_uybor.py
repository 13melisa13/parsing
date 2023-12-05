
import random
import time
import requests
from PyQt6.QtCore import QThread, pyqtSignal

from models.commerce import Commerce
from models.flat import Flat, REPAIR_CHOICES_UYBOR
from config import BASE_API, headers
from models.land import Land


def json_uybor(page=0, limit=100, cat=7):
    url = "https://api.uybor.uz/api/v1/listings"
    params = {
        "limit": limit,
        "page": page,
        "mode": "search",
        "order": "-createdAt",
        "embed": "category,residentialComplex,region,city,district,zone,street,metro",
        "operationType__eq": "sale",
        "category__eq": cat
    }
    request = requests.get(url, params, headers=headers).json()

    return request["results"], request["total"]


class UploadUybor(QThread): #TODO
    db_res = []
    enable_to_post = True
    # finished = pyqtSignal(str)


    def awake_(self):
        self.enable_to_post = True
        print("wake up upload uybor")

    def sleep_(self):
        # asyncio.sleep(10)
        self.enable_to_post = False
        print("sleeeeep upload uybor")

    def __init__(self, db_res, real_estate_type):
        super().__init__()
        self.update_db(db_res)
        self.real_estate_type = real_estate_type
        # log_out = open('_internal/output/log_out_post_uybor.txt', 'a', encoding="utf-8")
        # log_err = open('_internal/output/log_out_post_uybor.txt', 'a', encoding="utf-8")
        # sys.stdout = log_out
        # sys.stderr = log_err

    def update_db(self, db_res):
        self.db_res = db_res

    def switch_url(self):
        match self.real_estate_type:
            case 'flat':
                return 'post_flats'
            case 'commerce':
                return 'post_commerces'
            case 'land':
                return 'post_lands'

    def run(self):
        time.sleep(120)
        # try:
        #     is_act = requests.get("http://prodamgaraj.ru:8000/is_active?wrong_type_of_market=True")
        #     print("is active", datetime.datetime.now(), is_act.status_code)
        # except Exception:
        #     print("try to is active", datetime.datetime.now())
        delay = random.randint(100, 1000)
        print("start post uybor")
        page = 0
        prev_res = 0
        total = 1000000
        limit = 100
        flats_to_post = []
        while prev_res < total:

            try:
                if limit > (total - prev_res):
                    limit = total - prev_res
                    # print(limit)
                match self.real_estate_type:
                    case 'flat':
                        results, total = json_uybor(page, limit, 7)
                    case 'commerce':
                        results, total = json_uybor(page, limit, 10)
                    case 'land':
                        results, total = json_uybor(page, limit, 11)

                print(prev_res, total, "upload uybor with limit",limit, "on page", page )
            except Exception as err:
                print(err)
                # time.sleep(1)
                time.sleep(1)

                continue

            for i in range(len(results)):
                flats_to_post.append(self.handle(results[i]))
            prev_res += len(results)
            page += 1
            # print(len(results))
            if len(flats_to_post) >= 500 or (total - prev_res < 500):
                while True:
                    try:
                        url = BASE_API + self.switch_url()
                        if not self.enable_to_post:
                            time.sleep(10)
                            print("Sleeep on 10 in upload uybor")
                            continue
                        rut =    [  flat  for flat in flats_to_post
                                              if flats_to_post.count(flat)<2]
                        flats_to_post_dict = [flat.prepare_to_dict()
                                              for flat in flats_to_post
                                              if flat not in self.db_res]
                        print("for post", self.real_estate_type, "uybor", len(rut))

                        post_r = requests.post(url=url, json=flats_to_post_dict, headers=headers)

                        if post_r.status_code != 200:
                            time.sleep(1)
                            print(f"unsuccessful code {self.real_estate_type}_uybor for post", post_r.status_code)
                            if post_r.status_code == 504:
                                continue
                            print(post_r.text)
                            break
                        flats_to_post = []
                        break
                    except Exception as err:
                        print(err)
                        time.sleep(1)
                        continue
        # self.finished.emit(self.real_estate_type)

    def handle(self, result):
        address = ''
        if result['zone'] is not None:
            address += result['zone']['name']['ru']
        if result['region'] is not None:
            address += ' ' + result['region']['name']['ru']
        if result['cityId'] is not None:
            address += ' ' + result['city']['name']['ru']
        if result['district'] is not None:
            address += ' ' + result['district']['name']['ru']
        if result['metro'] is not None:
            address += ' ' + result['metro']['name']['ru']
        if result['residentialComplex'] is not None:
            address += ' ' + result['residentialComplex']['name']['ru']
        if result['address'] is not None:
            address += ' ' + result['address']
        match self.real_estate_type:

            case 'flat':
                if result['repair'] is not None:
                    repair = REPAIR_CHOICES_UYBOR[result['repair']]
                else:
                    repair = REPAIR_CHOICES_UYBOR['repair']
                if result['isNewBuilding']:
                    is_new_building = 'Новостройка'
                else:
                    is_new_building = 'Вторичный'
                if not isinstance(result['room'], int):
                    room = result['room']
                else:
                    if result['room'] == 'freeLayout':
                        room = 'Студия'
                    else:
                        room = ''
                return Flat(
                    url=f'https://uybor.uz/listings/{result["id"]}',
                    square=float(result['square']),
                    floor=f'{result["floor"]}',
                    total_floor=f'{result["floorTotal"]}',
                    address=address,
                    repair=repair,
                    is_new_building=is_new_building,
                    room=room,
                    modified=result['updatedAt'],
                    price_uye=result['prices']['usd'],
                    price_uzs=result['prices']['uzs'],
                    description=result['description'],
                    id=result['id'],
                    domain="uybor"
                )
            case 'land':
                return Land(
                    url=f'https://uybor.uz/listings/{result["id"]}',
                    square=float(result['squareGround']),
                    type_of_land='',
                    location_feature='',
                    address=address,
                    modified=result['updatedAt'],
                    price_uye=result['prices']['usd'],
                    price_uzs=result['prices']['uzs'],
                    description=result['description'],
                    id=result['id'],
                    domain="uybor"
                )
            case 'commerce':
                sub = ''
                match result['subCategoryId']:
                    case 18:
                        sub = "Магазины/бутики,Салоны,Рестораны/кафе/бары"
                    case 12:
                        sub = "Офисы"
                    case 19:
                        sub = "Отдельно стоящие здания"
                    case 21:
                        sub = 'Склады'
                    case 17:
                        sub = 'Помещения промышленного назначения'
                return Commerce(
                    url=f'https://uybor.uz/listings/{result["id"]}',
                    square=float(result['square']),
                    type_of_commerce=sub,
                    address=address,
                    modified=result['updatedAt'],
                    price_uye=result['prices']['usd'],
                    price_uzs=result['prices']['uzs'],
                    description=result['description'],
                    id=result['id'],
                    domain="uybor"
                )


