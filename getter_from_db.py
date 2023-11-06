import datetime
import math
import time
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
        print("from db")
        page = 0
        prev_res = 0
        total = 1000000
        limit = 5000
        # print()
        flats = []
        while prev_res < total:
            # print(page, limit)
            try:
                if limit > (total - prev_res):
                    limit = total - prev_res
                results, total = json_db(page, limit, domain)
                print(total, prev_res, "db", domain)

                if total == 0:
                    # self.label.emit(f"Процесс: Обновление {domain} - Завершение с ошибкой")
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
                self.updated.emit(math.ceil((i + prev_res) * 100 / total))
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
            # print(flats[0].domain)
            # datetime.datetime.date()
            prev_res += len(results)
            self.init_flats.emit(flats)
            page += 1
        return flats
