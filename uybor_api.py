import os
import sys
from datetime import datetime

import requests
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QMessageBox

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
        "order": "upAt",
        "embed": "category,residentialComplex,region,city,district,zone,street,metro",
        "operationType__eq": "sale",
        "category__eq": "7"
    }
    request = requests.get(url, params).json()
    return request["results"]


def header_sheet(sheet):
    sheet.append(header)


def fill_sheet_uybor(sheet, progress, agrs=[]):
    # header_sheet(sheet)
    page = 0
    while True:
        # print("start")
        results = json_uybor(page)
        if len(results) == 0:
            return
        for i in range(len(results)):
            progress.setProperty("value", i * 100 / len(results))

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
                    results[i]['description']
            )
            sheet.append(row)
            # print(address)
        return  # TOdo remove
        page += 1


class ApiParser(QThread):
    def __init__(self, path='_internal/output/internal/', main_window=None):
        super().__init__()
        self.path = path
        self.main_window = main_window

    def run(self):
        self.main_window.update_uybor.setCheckable(False)
        self.main_window.update_uybor.setDisabled(True)
        self.main_window.update_all_data.setDisabled(True)
        book = read_excel_template(self.main_window)
        sheet = book[book.sheetnames[0]]
        sheet.title = f"{datetime.now().strftime('%d.%m.%y_%H.%M')}"
        if not os.path.exists(self.path):
            self.main_window.message.setText(f"Повреждена файловая система! Перезагрузите приложение")
            self.main_window.message.setIcon(QMessageBox.Icon.Critical)
            self.main_window.message.exec()
            sys.exit()
        # self.main_window.label_progress_bar.setText("Процесс: Обновление UyBor")
        self.main_window.progress_bar.setProperty("value", 0)
        # header_sheet(sheet)
        fill_sheet_uybor(sheet, self.main_window.progress_bar)
        self.path += f'uybor.xlsm'
        if os.path.exists(self.path):
            os.remove(self.path)
        book.save(self.path)
        # self.main_window.label_progress_bar.setText("Процесс: Обновление UyBor - Завершено")
        self.main_window.progress_bar.setProperty("value", 100)
        self.main_window.update_uybor.setDisabled(False)
        self.main_window.update_uybor.setCheckable(True)
        self.main_window.update_all_data.setDisabled(False)
        self.main_window.filter_button_clicked()
        self.main_window.time_last.setText(f"{self.main_window.time_fixed.currentTime().toString()}")
        # print(self.main_window.time_last, f"{datetime.now().strftime('%d%m%y%H:%M')}")




