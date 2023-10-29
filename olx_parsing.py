import math
import os
import re
# import logging
import time
from urllib.request import urlopen, Request
from PyQt6.QtCore import QThread, pyqtSignal
# from PyQt6.QtWidgets import QMessageBox
from bs4 import BeautifulSoup
import datetime

from main import read_excel_template
#
# logger = loggingbasicConfig(filename="MAEParser.log",
#                     encoding="utf-8",
#                     filemode='a',
#                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                     datefmt='%H:%M:%S')
class Flat:
    def __init__(self,
                 price_uye=1.0,
                 price_uzs=1.0,
                 square=1.0,
                 room='',
                 floor='',
                 total_floor='',
                 address="default",
                 modified=datetime.datetime.now(),
                 url="https://www.olx.uz",
                 repair="repair",
                 is_new_building=False,
                 description=""):
        self.price_uye = float(price_uye)
        self.price_uzs = float(price_uzs)
        try:
            self.price_per_meter_uzs = "%.2f" % (float(price_uzs) / float(square))
            self.price_per_meter_uye = "%.2f" % (float(price_uye) / float(square))
        except Exception:
            self.price_per_meter_uye = 'default'
            self.price_per_meter_uzs = 'default'
        self.square = float(square.__str__().replace(" ", ''))
        self.description = description
        self.floor = floor
        self.room = room
        self.total_floor = total_floor
        self.address = address
        self.repair = repair
        self.is_new_building = is_new_building
        self.modified = modified
        self.url = url

    def prepare_to_list(self):
        return [
            self.url,
            self.square,
            f'{self.floor}/{self.total_floor}',
            self.address,
            self.repair,
            self.is_new_building,
            self.room,
            self.modified,
            self.price_uye,
            self.price_per_meter_uye,
            self.price_uzs,
            self.price_per_meter_uzs,
            self.description
        ]

    def __str__(self):
        return f'{self.price_uzs}; {self.price_uye}; {self.url}'
        # f' {self.modified}; {self.url}; {self.address}; '
        # f'{self.square}; {self.price_per_meter_uzs}; {self.price_per_meter_uye}; {self.repair};'
        # f' {self.floor}/{self.total_floor}; {self.room}')


def get_rate():
    url = 'https://ofb.uz/uz/'
    Request(url).add_header('Accept-Encoding', 'identity')
    page = urlopen(url)
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    curs = soup.find_all(name="div", attrs={"class": "currency"})
    return float(re.search(r"(\d+)\.(\d+)", curs[0].get_text())[0])


def get_all_flats_from_html(url, page, progress, max_page, prev_count):  # UZS -сумм., UYE - y.e.
    list_of_flats = []
    url = url + f'?currency=UYE&page={page}'
    req = Request(url)
    req.add_header('Accept-Encoding', 'identity')
    page = urlopen(url)
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    ads = soup.find_all(name="div", attrs={"data-cy": "l-card"})

    # rate = requests.get("https://cbu.uz/ru/arkhiv-kursov-valyut/json/USD/").json()[0]['Rate']
    rate = get_rate()
    for ad in ads:
        # print(math.floor((ads.index(ad)+prev_count) * 100 / len(ads) / max_page))
        progress.emit(math.ceil((ads.index(ad)+prev_count) * 100 / len(ads) / max_page))
        address_with_modified = ad.find(name='p', attrs={"data-testid": "location-date"}).get_text().split(" - ")
        price_uye = ad.find(name='p', attrs={"data-testid": "ad-price"}).get_text().split(" ")
        if price_uye is None:
            price_uye = 1
        square = ad.find(name='div', attrs={"color": "text-global-secondary"}).get_text()
        final_price = 0
        for i in range(0, len(price_uye) - 1):
            final_price += (int(price_uye[len(price_uye) - 2 - i]) * math.pow(1000, i))

        if "Сегодня" in address_with_modified[1]:
            now = datetime.datetime.now()
            address_with_modified[1] = f'{now.day} {now.strftime("%B").lower()} {now.year}г.'
        details = get_details_of_flat("https://www.olx.uz" + ad.a.get("href"))
        # print(details['floor'], "floor", ad.a.get("href"))

        flat = Flat(
            price_uye=final_price,
            price_uzs=float(rate) * float(final_price),
            square=square,
            address=address_with_modified[0],
            modified=address_with_modified[1],
            url="https://www.olx.uz" + ad.a.get("href"),
            room=details['room'],
            floor=details['floor'],
            total_floor=details['total_floor'],
            repair=details['repair'],
            is_new_building=details['is_new_building'],
            description=details['description']
        )
        list_of_flats.append(flat)
    return list_of_flats


def get_details_of_flat(url):
    req = Request(url)
    req.add_header('Accept-Encoding', 'identity')
    page = urlopen(url)
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    ad = soup.find(name="div", attrs={"data-testid": "main"}).find(name="ul").get_text()  # li p parse
    ad_desc = soup.find(name="div", attrs={"data-cy": "ad_description", }).find(name="div").get_text()
    # print(ad_desc, url)
    details = {
        "room": re.search(r"комнат: (\d+)", ad),
        "floor": re.search(r"Этаж: (\d+)", ad),
        "total_floor": re.search(r"Этажность дома: (\d+)", ad),
        "repair": re.search(r"Ремонт: ([А-Я][а-я]+\s*[а-я]*)", ad),
        "is_new_building": re.search(r"жилья: ([А-Я][а-я]+)", ad),
        "description": ad_desc.replace("\n", ";")
    }
    # print(details['repair'])
    for detail in details:
        if details[detail] is not None:
            if detail != "description":
                details[detail] = details[detail][1]
        else:
            details[detail] = ''
    return details


class OlxParser(QThread):
    updated = pyqtSignal(int)
    throw_exception = pyqtSignal(str)
    block_export = pyqtSignal(bool, str)
    block_closing = pyqtSignal(bool)

    def __init__(self, path='_internal/output/internal/'):
        super().__init__()
        self.path = path

    def run(self):

        self.block_closing.emit(True)
        book = read_excel_template(self.throw_exception)
        sheet = book[book.sheetnames[0]]
        sheet.title = f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}"
        if not os.path.exists(self.path):
            self.throw_exception.emit("Повреждена файловая система! Перезагрузите приложение")

        # header_sheet(sheet)
        url = "https://www.olx.uz/nedvizhimost/kvartiry/prodazha/"
        req = Request(url)
        req.add_header('Accept-Encoding', 'identity')
        html = urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        max_page = soup.find_all(name="li", attrs={"data-testid": "pagination-list-item"})
        max_page = int(max_page[len(max_page) - 1].get_text())
        page = 1
        start = time.time()
        # max_page = 3  # TODO test_data
        prev_count = 0
        while page <= max_page:
            results = get_all_flats_from_html(url, page, self.updated, max_page, prev_count)

            for i in range(0, len(results)):
                sheet.append(results[i].prepare_to_list())
            time.sleep(1)
            # print(time.time() - start)
            page += 1
            prev_count += len(results)
        self.path += f'olx.xlsm'
        self.block_export.emit(True, "olx")
        if os.path.exists(self.path):
            os.remove(self.path)
        book.save(self.path)
        self.block_export.emit(False, "olx")
        self.block_closing.emit(False)





