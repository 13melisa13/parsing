from datetime import datetime

from models.real_estate import RealEstate

REPAIR_CHOICES_UYBOR = {
    "repair": "Ремонт",
    "custom": "Авторский проект",
    "sredniy": "Средний",
    "kapital": "Требует ремонта",
    "chernovaya": "Черновая отделка",
    "predchistovaya": "Предчистовая отделка",
    "evro": "Евроремонт"
}

header_flat = [
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
    "Описание",
    "Категория"
]


class Flat(RealEstate):
    def __init__(self,
                 price_uye=1.0,
                 price_uzs=1.0,
                 square=1.0,
                 address="default",
                 modified=datetime.now().__str__(),
                 url="https://www.olx.uz",
                 description="",
                 id=0,
                 domain="",
                 is_active=True,
                 room='',
                 floor='',
                 total_floor='',
                 repair="repair",
                 category="Продажа",
                 is_new_building=False):
        super().__init__(price_uye=price_uye,
                         price_uzs=price_uzs,
                         square=square,
                         address=address,
                         modified=modified,
                         url=url,
                         description=description,
                         id=id,
                         domain=domain,
                         is_active=is_active,
                         category=category)
        self.floor = floor
        self.room = room
        self.total_floor = total_floor
        self.repair = repair
        self.is_new_building = is_new_building

    def prepare_to_list(self):
        return [
            self.url.__str__(),
            self.square.__str__(),
            f'{self.floor}/{self.total_floor}',
            self.address.__str__(),
            self.repair.__str__(),
            self.is_new_building.__str__(),
            self.room.__str__(),
            self.modified.__str__(),
            self.price_uye.__str__(),
            self.price_per_meter_uye.__str__(),
            self.price_uzs,
            self.price_per_meter_uzs.__str__(),
            self.description.__str__(),
            self.category.__str__()
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
            "modified": self.modified.__str__(),
            "price_uye": self.price_uye,
            "price_uzs": self.price_uzs,
            "description": self.description,
            "external_id": self.external_id,
            "domain": self.domain,
            "is_active": self.is_active,
            "category": self.category
        }

    def __str__(self):
        return self.__dict__
