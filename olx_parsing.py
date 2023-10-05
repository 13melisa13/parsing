import math
import re
import time
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import datetime

from uybor_api import header_sheet


class Flat:
    def __init__(self,
                 price_uye=1,
                 price_uzs=1,
                 square=1,
                 address="default",
                 modified=datetime.datetime.now(),
                 url="https://www.olx.uz",
                 room=1,
                 floor=1,
                 total_floor=1,
                 repair="repair",
                 is_new_building=False):
        self.price_uye = price_uye
        self.price_uzs = price_uzs
        try:
            self.price_per_meter_uzs = float(price_uzs) / float(square)
            self.price_per_meter_uye = float(price_uye) / float(square)
        except Exception:
            self.price_per_meter_uye = 'default'
            self.price_per_meter_uzs = 'default'
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
        return f'{self.price_uzs}; {self.price_uye}; {self.url}'
        # f' {self.modified}; {self.url}; {self.address}; '
        # f'{self.square}; {self.price_per_meter_uzs}; {self.price_per_meter_uye}; {self.repair};'
        # f' {self.floor}/{self.total_floor}; {self.room}')


def get_all_flats_from_html(url, page):  # UZS -сумм., UYE - y.e.
    list_of_flats = []
    url1 = url + f'?currency=UYE&page={page}'
    url += f'?currency=UZS&page={page}'
    req = Request(url)
    req.add_header('Accept-Encoding', 'identity')
    page = urlopen(url)
    page1 = urlopen(url1)
    html = page.read().decode('utf-8')
    html1 = page1.read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    soup1 = BeautifulSoup(html1, "html.parser")
    ads = soup.find_all(name="div", attrs={"data-cy": "l-card"})
    ads1 = soup1.find_all(name="div", attrs={"data-cy": "l-card"})
    for ad in ads:
        ad1 = ads1[ads.index(ad)]
        address_with_modified = ad.find(name='p', attrs={"data-testid": "location-date"}).get_text().split(" - ")
        price1 = ad.find(name='p', attrs={"data-testid": "ad-price"}).get_text().split(" ")
        price2 = ad1.find(name='p', attrs={"data-testid": "ad-price"}).get_text().split(" ")
        square = ad.find(name='div', attrs={"color": "text-global-secondary"}).get_text()
        final_price1 = 0
        for i in range(0, len(price1) - 1):
            final_price1 += (int(price1[len(price1) - 2 - i]) * math.pow(1000, i))
        final_price2 = 0
        for i in range(0, len(price2) - 1):
            final_price2 += (int(price2[len(price2) - 2 - i]) * math.pow(1000, i))
        if "Сегодня" in address_with_modified[1]:
            now = datetime.datetime.now()
            address_with_modified[1] = f'{now.day} {now.strftime("%B").lower()} {now.year}г.'
        details = get_details_of_flat("https://www.olx.uz" + ad.a.get("href"))
        flat = Flat(
            price_uye=final_price2,
            price_uzs=final_price1,
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
        "repair": re.search(r"Ремонт: ([А-Я][а-я]+)", ad), # TODO repair check
        "is_new_building": re.search(r"жилья: ([А-Я][а-я]+)", ad),
    }
    for detail in details:
        if details[detail] is not None:
            details[detail] = details[detail][1]
        else:
            details[detail] = ''
    return details

# TODO fix price
def fill_sheet_olx(sheet, agrs=[]):
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
    max_page = 1  # TODO max-page
    while page <= max_page:
        results = get_all_flats_from_html(url, page)
        for i in range(0, len(results)):
            sheet.append([results[i].price_uye
                             , results[i].price_per_meter_uye
                             , results[i].price_uzs
                             , results[i].price_per_meter_uzs
                             , results[i].square
                             , f'{results[i].floor}/{results[i].total_floor}'
                             , results[i].address
                             , results[i].repair
                             , results[i].is_new_building
                             , results[i].room
                             , results[i].url
                             , results[i].modified])

        print(f'page:{page}  time: {time.time() - start}')
        time.sleep(10)
        page += 1
