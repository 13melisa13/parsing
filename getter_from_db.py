import math
import random
import time
import datetime
import pytz
import requests
from PyQt6.QtCore import pyqtSignal, QThread

from config import BASE_API, headers
from models.commerce import Commerce
from models.flat import Flat
from models.land import Land


def json_db(page=0, limit=5000, domain="uybor", url_=''):
    print(limit)
    url = BASE_API + url_
    params = {
        "limit": limit,
        "page": page,
        "domain": domain
    }
    # session = requests.Session()
    # retry = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
    # adapter = HTTPAdapter(max_retries=retry)
    # session.mount('http://', adapter)
    # session.mount('https://', adapter)

    print(f"Запрос на сервак {url_} {domain} {datetime.datetime.now().time()}")
    response = requests.get(url, params=params, headers=headers, timeout=20)

    # response = requests.get(url, params=params, headers=headers)
    print(f"Ответ сервака {url_} {domain} {datetime.datetime.now().time()} {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"TRY AGAIN {response.status_code} {domain}")
    # else:
    # print(response.text)
    return response.json()["data"], response.json()["active_data_len"]


class DataFromDB(QThread):
    updated = pyqtSignal(int, str, str)
    throw_exception = pyqtSignal(str, str, str)
    throw_info = pyqtSignal(str)
    label = pyqtSignal(str, str, str)
    date = pyqtSignal(list, str, str)
    block_closing = pyqtSignal(bool)
    init_flats = pyqtSignal(list, str, str)
    # finished = pyqtSignal(str, str)

    def __init__(self, domain, rate=1.0, real_estate_type='flat'):
        super().__init__()
        self.domain = domain
        self.rate = rate
        self.real_estate_type = real_estate_type
        print("RaTe: ", rate)

    def run(self):
        type_ = self.real_estate_type
        d = self.domain
        self.updated.emit(1, type_, d)
        self.label.emit(f"Процесс: Обновление {self.domain}", type_, d)
        self.block_closing.emit(True)
        self.date.emit(self.get_db(self.domain, type_), type_, d)
        self.updated.emit(100, type_, d)
        self.label.emit(f"Процесс: Обновление {self.domain} - Завершено", type_, d)
        self.block_closing.emit(False)
        # self.finished.emit(type_, d)

    def switch_url(self):
        match self.real_estate_type:
            case 'flat':
                return 'get_flats'
            case 'commerce':
                return 'get_commerces'
            case 'land':
                return 'get_lands'

    def get_db(self, domain, real_estate_type):

        page = 0
        prev_res = 0
        total = 10000000
        limit = 2000
        # print()
        tz = pytz.timezone('Asia/Tashkent')
        real_estates = []
        while prev_res < total:
            # print(page, limit)
            try:
                self.label.emit(f"Процесс: Обновление {self.domain}", real_estate_type, domain)
                if limit > (total - prev_res):
                    limit = total - prev_res
                results, total = json_db(page, limit, domain, self.switch_url())
                print(f"{datetime.datetime.now(tz=tz)} db_{real_estate_type} {domain} with limit", limit, "page", page)
                if not results:
                    break
                if total == 0:
                    # self.label.emit(f"Процесс: Обновление {domain} - Завершение с ошибкой")
                    return []
            except Exception as err:
                self.label.emit(f"Процесс: Обновление {domain} - Переподключение", real_estate_type, domain)
                # self.throw_info.emit("Проблемы с подключением к сети")
                print("ERR", err)
                time.sleep(random.randint(0, 10))
                continue
                # break
            self.label.emit(f"Процесс: Обновление {domain}", real_estate_type, domain)
            # print("res", results, total)
            for i in range(len(results)):
                # print("QWER", self.rate * results[i]['price_uye'], self.rate , results[i]['price_uye'])

                real_estate_obj = self.real_estate_obj(results[i])
                real_estates.append(real_estate_obj)
                self.updated.emit(math.ceil((i + prev_res) * 100 / total), real_estate_type, domain)
            # print(flats[0].domain)
            # datetime.datetime.date()
            prev_res += len(results)
            self.init_flats.emit(real_estates, real_estate_type, domain)
            page += 1
        return real_estates

    def real_estate_obj(self, result):
        if result['price_uzs'] == 0:
            price_uzs = self.rate * result['price_uye']
        else:
            price_uzs = result['price_uzs']
        match self.real_estate_type:
            case 'flat':
                return Flat(
                    url=result["url"],
                    square=float(result['square']),
                    floor=f'{result["floor"]}',
                    total_floor=f'{result["total_floor"]}',
                    address=result["address"],
                    repair=result["repair"],
                    is_new_building=result['is_new_building'],
                    room=result['room'],
                    modified=result['modified'],
                    price_uye=result['price_uye'],
                    price_uzs=price_uzs,
                    description=result['description'],
                    id=result['external_id'],
                    domain=result["domain"],
                    is_active=result["is_active"])
            case 'commerce':
                return Commerce(
                    url=result["url"],
                    square=float(result['square']),
                    address=result["address"],
                    type_of_commerce=result['type_of_commerce'],
                    modified=result['modified'],
                    price_uye=result['price_uye'],
                    price_uzs=price_uzs,
                    description=result['description'],
                    id=result['external_id'],
                    domain=result["domain"],
                    is_active=result["is_active"])
            case 'land':
                return Land(
                    url=result["url"],
                    square=float(result['square']),
                    address=result["address"],
                    type_of_land=result['type_of_land'],
                    location_feature=result['location_feature'],
                    modified=result['modified'],
                    price_uye=result['price_uye'],
                    price_uzs=price_uzs,
                    description=result['description'],
                    id=result['external_id'],
                    domain=result["domain"],
                    is_active=result["is_active"])
            case _:
                return None
