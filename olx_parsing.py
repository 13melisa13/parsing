import math
import re
import time
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import datetime
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU')


class Flat:
    def __init__(self,
                 price=1,
                 square=1,
                 address="default",
                 modified=datetime.datetime.now(),
                 url="https://www.olx.uz",
                 room=1,
                 floor=1,
                 total_floor=1,
                 repair="repair",
                 is_new_building=False):
        self.price = price
        try:
            self.price_per_meter = float(price) / float(square)
        except Exception:
            self.price_per_meter = 'default'
        self.square = square
        self.floor = floor
        self.room = room
        self.total_floor = total_floor
        self.address = address
        self.repair = repair
        self.is_new_building = is_new_building
        self.modified = modified
        self.url = url

    def __str__(self):
        return (f'{self.price}; {self.modified}; {self.url}; {self.address}; '
                f'{self.square}; {self.price_per_meter}; {self.repair};'
                f' {self.floor}/{self.total_floor}; {self.room}')


def get_all_flats_from_html(url, currency, page):  # UZS -сумм., UYE - y.e.
    list_of_flats = []
    url += f'?currency={currency}&page={page}'
    req = Request(url)
    req.add_header('Accept-Encoding', 'identity')
    page = urlopen(url)
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    ads = soup.find_all(name="div", attrs={"data-cy": "l-card"})
    for ad in ads:
        address_with_modified = ad.find(name='p', attrs={"data-testid": "location-date"}).get_text().split(" - ")
        price = ad.find(name='p', attrs={"data-testid": "ad-price"}).get_text().split(" ")
        square = ad.find(name='div', attrs={"color": "text-global-secondary"}).get_text()
        final_price = 0
        for i in range(0, len(price) - 1):
            final_price += (int(price[len(price) - 2 - i]) * math.pow(1000, i))
        if "Сегодня" in address_with_modified[1]:
            now = datetime.datetime.now()
            address_with_modified[1] = f'{now.day} {now.strftime("%B").lower()} {now.year}г.'
        details = get_details_of_flat("https://www.olx.uz" + ad.a.get("href"))
        flat = Flat(
            price=final_price,
            square=square,
            address=address_with_modified[0],
            modified=address_with_modified[1],
            url="https://www.olx.uz" + ad.a.get("href"),
            room=details['room'],
            floor=details['floor'],
            total_floor=details['total_floor'],
            repair=details['repair'],
            is_new_building=details['is_new_building']
        )
        # print(flat)
        list_of_flats.append(flat)
    return list_of_flats


def get_details_of_flat(url):
    req = Request(url)
    req.add_header('Accept-Encoding', 'identity')
    page = urlopen(url)
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    ad = soup.find(name="div", attrs={"data-testid": "main"}).find(name="ul").get_text()  # li p parse
    details = {
        "room": re.search(r"комнат: (\d+)", ad),
        "floor": re.search(r"Этаж: (\d+)", ad),
        "total_floor": re.search(r"Этажность дома: (\d+)", ad),
        "repair": re.search(r"Ремонт: ([А-Я][а-я]+)", ad),
        "is_new_building": re.search(r"жилья: ([А-Я][а-я]+)", ad),
    }
    for detail in details:
        if details[detail] is not None:
            details[detail] = details[detail][1]
        else:
            details[detail] = ''
    return details


def fill_sheet_olx(sheets):
    cur = ['UYE', 'UZS']
    header = [
        "цена",
        "цена за метр",
        "мерты",
        "этаж",
        "address",
        'кол-во комнаты',
        "ремонт",
        "тип жилья",
        "ссылка",
        "дата обновления",
    ]
    for i in range(len(header)):
        for sheet in sheets:
            sheet.write(0, i, header[i])

    url = "https://www.olx.uz/nedvizhimost/kvartiry/prodazha/"
    req = Request(url)
    req.add_header('Accept-Encoding', 'identity')
    html = urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    max_page = soup.find_all(name="li", attrs={"data-testid": "pagination-list-item"})
    max_page = int(max_page[len(max_page) - 1].get_text())
    delta = 1
    page = 1
    start = time.time()
    max_page = 1  #TODO убрать
    while page <= max_page:
        for sheet in sheets:
            results = get_all_flats_from_html(url, cur[sheets.index(sheet)], page)
            for i in range(0, len(results)):
                sheet.write(i + delta, 0, results[i].price)
                sheet.write(i + delta, 1, results[i].price_per_meter)
                sheet.write(i + delta, 2, results[i].square)
                sheet.write(i + delta, 3, f'{results[i].floor}/{results[i].total_floor}')
                sheet.write(i + delta, 4, results[i].address)
                sheet.write(i + delta, 5, results[i].room)
                sheet.write(i + delta, 6, results[i].repair)
                sheet.write(i + delta, 7, results[i].is_new_building)
                sheet.write(i + delta, 8, results[i].url)
                sheet.write(i + delta, 9, results[i].modified)
            print(f'page:{page} sheet:{(sheets.index(sheet) + 1)}  time: {time.time() - start}')
            time.sleep(10)
        delta += len(results)
        page += 1

