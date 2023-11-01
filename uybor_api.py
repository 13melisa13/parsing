import math
import os
import time
from datetime import datetime
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from main import read_excel_template

REPAIR_CHOICES_UYBOR = {
    "repair": "Ремонт",
    "custom": "Авторский проект",
    "sredniy": "Средний",
    "kapital": "Требует ремонта",
    "chernovaya": "Черновая отделка",
    "predchistovaya": "Предчистовая отделка",
    "evro": "Евроремонт"
}
CURRENCY_CHOISES = [
    "СУММ.", "У.Е."
]
header = [
        "Ссылка",
        "Площадь",
        "Этаж",
        "Адрес",
        "Ремонт",
        "Новостройка",
        'Кол-во комнат',
        "Дата обновления",
        "Цена, $",
        "Цена за метр, $",
        "Цена, сумм",
        "Цена за метр, сумм",
        "Описание"
    ]


def json_uybor(page=0, limit=100):
    # усл ед "usd"
    # суммы "uzs"
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


class ApiParser(QThread):
    block_export = pyqtSignal(bool, str)
    updated = pyqtSignal(int)
    throw_exception = pyqtSignal(str)
    throw_info = pyqtSignal(str)
    label = pyqtSignal(str)
    date = pyqtSignal()
    block_closing = pyqtSignal(bool)

    def __init__(self, path='_internal/output/internal/'):
        super().__init__()
        self.path = path

    def run(self):
        self.updated.emit(0)
        self.label.emit("Процесс: Обновление UyBor")
        self.block_closing.emit(True)
        book = read_excel_template(self.throw_exception)
        sheet = book[book.sheetnames[0]]
        sheet.title = f"{datetime.now().strftime('%d.%m.%y_%H.%M')}"
        if not os.path.exists(self.path):
            self.throw_exception.emit("Повреждена файловая система! Перезагрузите приложение")
        self.fill_sheet_uybor(sheet)
        self.path += f'uybor.xlsm'
        self.block_export.emit(True, "uybor")
        if os.path.exists(self.path):
            os.remove(self.path)
        book.save(self.path)
        self.date.emit()
        self.updated.emit(100)
        self.label.emit("Процесс: Обновление UyBor - Завершено")
        self.block_export.emit(False, "uybor")
        self.block_closing.emit(False)

    def fill_sheet_uybor(self, sheet):
        page = 0
        prev_res = 0
        total = 10000
        limit = 100
        while prev_res < total:
            try:
                if limit > (total - prev_res):
                    limit = total - prev_res
                results, total = json_uybor(page, limit)
            except Exception as err:
                # self.updated.emit(0)
                self.label.emit("Процесс: Обновление UyBor - Переподключение")
                self.throw_info.emit("Проблемы с подключением к сети")
                print(err)
                time.sleep(1)
                continue
            print("uybor ", page, total, prev_res, len(results))
            if len(results) == 0:
                break
            for i in range(len(results)):
                # print((i + prev_res) * 100 / total)
                # raise Exception(" Я В РОТ АПИ ВАШ")
                self.updated.emit(math.ceil((i + prev_res) * 100 / total))
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
                row = (
                    f'https://uybor.uz/listings/{results[i]["id"]}',
                    int(results[i]['square']),
                    f'{results[i]["floor"]}/{results[i]["floorTotal"]}',
                    address,
                    repair,
                    is_new_building,
                    room,
                    results[i]['updatedAt'],
                    results[i]['prices']['usd'],
                    results[i]['prices']['usd'] / results[i]['square'],
                    results[i]['prices']['uzs'],
                    results[i]['prices']['uzs'] / results[i]['square'],
                    results[i]['description'],
                    results[i]['id']
                )
                sheet.append(row)
            prev_res += len(results)
            page += 1



