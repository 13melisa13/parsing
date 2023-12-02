from datetime import datetime
from models.real_estate import RealEstate

COMMERCE_CHOICES = {
    "1": "Магазины/бутики",
    "2": "Салоны",
    "3": "Рестораны/кафе/бары",
    "4": "Офисы",
    "5": "Склады",
    "6": "Отдельно стоящие здания",
    "7": "Базы отдыха",
    "8": 'Помещения промышленного назначения',
    "9": 'Помещения свободного назначения',
    "10": 'МАФ (Малая архитектурная форма)',
    "11": 'Часть здания',
    "12": "Другое",
}
header_commerce = [
    "Ссылка",
    "Площадь",
    "Адрес",
    "Тип недвижимости",
    "Дата обновления",
    "Цена, $",
    "Цена за метр, $",
    "Цена, сумм",
    "Цена за метр, сумм"
]

class Commerce(RealEstate):
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
                 type_of_commerce=''
                 ):
        super().__init__(price_uye=price_uye,
                         price_uzs=price_uzs,
                         square=square,
                         address=address,
                         modified=modified,
                         url=url,
                         description=description,
                         id=id,
                         domain=domain,
                         is_active=is_active)
        self.type_of_commerce = type_of_commerce

    def prepare_to_list(self):
        return [
            self.url.__str__(),
            self.square.__str__(),
            self.address.__str__(),
            self.type_of_commerce,
            self.modified.__str__(),
            self.price_uye.__str__(),
            self.price_per_meter_uye.__str__(),
            self.price_uzs,
            self.price_per_meter_uzs.__str__(),
        ]

    def prepare_to_dict(self):
        return {
            "url": self.url,
            "square": self.square,
            "address": self.address,
            "type_of_commerce": self.type_of_commerce,
            "modified": self.modified.__str__(),
            "price_uye": self.price_uye,
            "price_uzs": self.price_uzs,
            "description": self.description,
            "external_id": self.external_id,
            "domain": self.domain,
            "is_active": self.is_active
        }

    def __str__(self):
        return self.__dict__
