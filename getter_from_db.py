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
    n_retries = 4,
    backoff_factor = 0.9,
    status_codes = [504, 503, 502, 500, 429]
    sess = requests.Session()
    n_retries = Retry(connect=n_retries, backoff_factor=backoff_factor,status_forcelist = status_codes)
    sess.mount("https://", HTTPAdapter(max_retries=n_retries))
    sess.mount("http://", HTTPAdapter(max_retries=n_retries))
    response = sess.get(url, params=params, verify=False, timeout=(3,7))
    print(response)
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
        self.label.emit("Процесс: Обновление UyBor")
        self.block_closing.emit(True)
        self.date.emit(self.get_db(self.domain))
        self.updated.emit(100)
        self.label.emit("Процесс: Обновление UyBor - Завершено")
        self.block_closing.emit(False)

    def get_db(self, domain):
        page = 0
        prev_res = 0
        total = 1
        limit = 1
        flats = []
        while prev_res < total:
            try:
                if limit > (total - prev_res):
                    limit = total - prev_res
                results, total = json_db(page, limit, domain)
                print(results, total)
                if total == 0:
                    self.label.emit(f"Процесс: Обновление {domain} - Завершение с ошибкой")
                    return
            except Exception as err:
                self.label.emit(f"Процесс: Обновление {domain} - Переподключение")
                # self.throw_info.emit("Проблемы с подключением к сети")
                print("ДА ЕПТ ТВОЮ МАТЬ", err)
                raise err
                time.sleep(15)
                continue
                # break
            self.label.emit(f"Процесс: Обновление {domain}")
            for i in range(len(results)):
                flats.append(Flat(
                    url={results[i]["url"]},
                    square=float(results[i]['square']),
                    floor=f'{results[i]["floor"]}',
                    total_floor=f'{results[i]["floorTotal"]}',
                    address=results[i]["address"],
                    repair=results[i]["repair"],
                    is_new_building=results[i]['is_new_building'],
                    room=results[i]['room'],
                    modified=results[i]['modified'],
                    price_uye=results[i]['price_usd'],
                    price_uzs=results[i]['price_uzs'],
                    description=results[i]['description'],
                    id=results[i]['id'],
                    domain=results[i]["domain"],
                    is_active=results[i]["is_active"]
                ))

            prev_res += len(results)
            page += 1
        print(flats)
        return flats
