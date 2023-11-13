
import random
import time
import requests
from PyQt6.QtCore import QThread

from flat import Flat, REPAIR_CHOICES_UYBOR, BASE_API, headers


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
    request = requests.get(url, params, headers=headers).json()

    return request["results"], request["total"]


class UploadUybor(QThread):
    db_res = []
    enable_to_post = True

    def awake_(self):
        self.enable_to_post = True
        print("wake up upload uybor")

    def sleep_(self):
        # asyncio.sleep(10)
        self.enable_to_post = False
        print("sleeeeep upload uybor")

    def __init__(self, db_res):
        super().__init__()
        self.update_db(db_res)
        # log_out = open('_internal/output/log_out_post_uybor.txt', 'a', encoding="utf-8")
        # log_err = open('_internal/output/log_out_post_uybor.txt', 'a', encoding="utf-8")
        # sys.stdout = log_out
        # sys.stderr = log_err

    def update_db(self, db_res):
        self.db_res = db_res

    def run(self):
        # time.sleep(120)
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
                    print(limit)
                results, total = json_uybor(page, limit)

                print(prev_res, total, "upload uybor")
            except Exception as err:
                print(err)
                # time.sleep(1)
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
                    is_new_building = 'Новостройка'
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
                    square=float(results[i]['square']),
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
            page += 1
            # print(len(results))
            if len(flats_to_post) >= 500 or (total - prev_res < 500):
                while True:
                    try:
                        url = BASE_API + "post_flats"
                        if not self.enable_to_post:
                            time.sleep(10)
                            print("Sleeep on 10 in upload uybor")
                            continue
                        flats_to_post_dict = [flat.prepare_to_dict()
                                              for flat in flats_to_post
                                              if flat not in self.db_res]
                        post_r = requests.post(url=url, json=flats_to_post_dict, headers=headers)

                        if post_r.status_code != 200:
                            time.sleep(1)
                            print(post_r.status_code)
                            continue
                        flats_to_post = []
                        break
                    except Exception as err:
                        print(err)
                        time.sleep(1)
                        continue


