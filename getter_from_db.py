import math
import sys
import time
import datetime

import pytz
import requests
from PyQt6.QtCore import pyqtSignal, QThread
from flat import Flat, BASE_API, headers


def json_db(page=0, limit=5000, domain="uybor"):
    print(limit)
    url = BASE_API + "get_flats"
    params = {
        "limit": limit,
        "page": page,
        "domain": domain
    }

    response = requests.get(url, params=params, headers=headers)
    print(response)
    if response.status_code != 200:
        raise Exception(f"TRY AGAIN {response.status_code} {domain}")
    return response.json()["data"], response.json()["data_length"]


class DataFromDB(QThread):
    updated = pyqtSignal(int)
    throw_exception = pyqtSignal(str)
    throw_info = pyqtSignal(str)
    label = pyqtSignal(str)
    date = pyqtSignal(list)
    block_closing = pyqtSignal(bool)
    init_flats = pyqtSignal(list)

    def __init__(self, domain, rate=1.0):
        super().__init__()
        self.domain = domain
        log_out = open('_internal/output/log_out.txt', 'a', encoding="utf-8")
        log_err = open('_internal/output/log_err.txt', 'a', encoding="utf-8")
        sys.stdout = log_out
        sys.stderr = log_err
        self.rate = rate

    def run(self):
        self.updated.emit(1)
        self.label.emit(f"Процесс: Обновление {self.domain}")
        self.block_closing.emit(True)
        self.date.emit(self.get_db(self.domain))
        self.updated.emit(100)
        self.label.emit(f"Процесс: Обновление {self.domain} - Завершено")
        self.block_closing.emit(False)

    def get_db(self, domain):
        page = 0
        prev_res = 0
        total = 1000000
        limit = 1000
        # print()
        tz = pytz.timezone('Asia/Tashkent')
        flats = []
        while prev_res < total:
            # print(page, limit)
            try:
                if limit > (total - prev_res):
                    limit = total - prev_res
                results, total = json_db(page, limit, domain)
                print(total, prev_res, "db", domain, datetime.datetime.now(tz))
                if total == 0:
                    # self.label.emit(f"Процесс: Обновление {domain} - Завершение с ошибкой")
                    return []
            except Exception as err:
                self.label.emit(f"Процесс: Обновление {domain} - Переподключение")
                # self.throw_info.emit("Проблемы с подключением к сети")
                print("ERR", err)
                time.sleep(1)
                continue
                # break
            self.label.emit(f"Процесс: Обновление {domain}")
            # print("res", results, total)
            for i in range(len(results)):
                if results[i]['price_uzs'] == 0:
                    price_uzs = self.rate * results[i]['price_uye']
                else:
                    price_uzs = results[i]['price_uzs']
                flats.append(Flat(
                    url=results[i]["url"],
                    square=float(results[i]['square']),
                    floor=f'{results[i]["floor"]}',
                    total_floor=f'{results[i]["total_floor"]}',
                    address=results[i]["address"],
                    repair=results[i]["repair"],
                    is_new_building=results[i]['is_new_building'],
                    room=results[i]['room'],
                    modified=results[i]['modified'],
                    price_uye=results[i]['price_uye'],
                    price_uzs=price_uzs,
                    description=results[i]['description'],
                    id=results[i]['external_id'],
                    domain=results[i]["domain"],
                    is_active=results[i]["is_active"]
                ))
                self.updated.emit(math.ceil((i + prev_res) * 100 / total))
            # print(flats[0].domain)
            # datetime.datetime.date()
            prev_res += len(results)
            self.init_flats.emit(flats)
            page += 1
        return flats
