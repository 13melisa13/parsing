from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


class Flat:
    def __init__(self, price, price_per_meter, square, floor, total_floor, address, name, modified, url):
        self.price = price
        self.price_per_meter = price_per_meter
        self.square = square
        self.floor = floor
        self.total_floor = total_floor
        self.address = address
        self.name = name
        self.modified = modified
        self.url = url


def get_all_flats_from_html(url):
    list_of_flats = []
    req = Request(url)
    req.add_header('Accept-Encoding', 'identity')
    page = urlopen(url)
    html = page.read().decode('unicode-escape').encode('latin1').decode('utf-8')
    soup = BeautifulSoup(page, "html.parser")
    print(soup.findAll('a', _class='MuiStack-root mui-style-9663hb'))
    file = open('file.html', 'w', encoding="utf-8")
    file.write(html)
    return list_of_flats
