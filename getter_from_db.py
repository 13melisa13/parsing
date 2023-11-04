import time

import requests
from PyQt6.QtCore import pyqtSignal, QThread
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from flat import Flat


def json_db(page=0, limit=100, domain="uybor"):
    # усл ед "usd"
    # суммы "uzs"

    url = "http://localhost:8000/get_flats/"
    params = {
        "limit": limit,
        "page": page,
        "domain": domain
    }

    response = requests.get(url, params=params)
    # print(response)
    return response.json()["data"], response.json()["data_length"]


class DataFromDB(QThread):
    updated = pyqtSignal(int)
    throw_exception = pyqtSignal(str)
    throw_info = pyqtSignal(str)
    label = pyqtSignal(str)
    date = pyqtSignal(list)
    block_closing = pyqtSignal(bool)

    def __init__(self, domain):
        super().__init__()
        self.domain = domain

    def run(self):
        self.updated.emit(0)
        self.label.emit(f"Процесс: Обновление {self.domain}")
        self.block_closing.emit(True)
        self.date.emit(self.get_db(self.domain))
        self.updated.emit(100)
        self.label.emit(f"Процесс: Обновление {self.domain} - Завершено")
        self.block_closing.emit(False)

    def get_db(self, domain):
        page = 0
        prev_res = 0
        total = 1
        limit = 1
        flats = []
        while prev_res < total:
            # print(page, limit)
            try:
                if limit > (total - prev_res):
                    limit = total - prev_res
                results, total = json_db(page, limit, domain)
                # print(results, total)
                if total == 0:
                    self.label.emit(f"Процесс: Обновление {domain} - Завершение с ошибкой")
                    return []
            except Exception as err:
                self.label.emit(f"Процесс: Обновление {domain} - Переподключение")
                # self.throw_info.emit("Проблемы с подключением к сети")
                print("ERR", err)
                time.sleep(15)
                continue
                # break
            self.label.emit(f"Процесс: Обновление {domain}")
            # print("res", results, total)
            for i in range(len(results)):
                # todo отсеять не активные зайждя на урл
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
                    price_uzs=results[i]['price_uzs'],
                    description=results[i]['description'],
                    id=results[i]['external_id'],
                    domain=results[i]["domain"],
                    is_active=results[i]["is_active"]
                ))
            prev_res += len(results)
            page += 1
        return flats
