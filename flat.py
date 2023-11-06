import datetime
import locale
BASE_API = 'https://ddm5q4hn-8000.euw.devtunnels.ms/'
locale.setlocale(locale.LC_TIME, 'ru_RU')
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
    # "Описание"
]

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.170",
    "accept": "*/*"
}


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
                 description="",
                 id=0,
                 domain="",
                 is_active=True):
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
        self.external_id = id
        self.domain = domain
        self.is_active = is_active

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
            # self.description,
            # self.external_id
        ]

    def prepare_to_dict(self):
        return {
            "url": self.url,
            "square": self.square,
            "floor": self.floor,
            "total_floor": self.total_floor,
            "address": self.address,
            "repair": self.repair,
            "is_new_building": self.is_new_building,
            "room": self.room,
            "modified": self.modified,
            "price_uye": self.price_uye,
            "price_uzs": self.price_uzs,
            "description": self.description,
            "id": self.external_id,
            "domain": self.domain,
            "is_active": self.is_active
        }

    def __str__(self):
        return self.__dict__
