from datetime import datetime
from models.real_estate import RealEstate

COMMERCE_CHOICES = [
    "Тип помещения",
    "Магазины/бутики",
    "Салоны",
    "Рестораны/кафе/бары",
    "Офисы",
    "Склады",
    "Отдельно стоящие здания",
    "Базы отдыха",
    'Помещения промышленного назначения',
    'Помещения свободного назначения',
    'МАФ (Малая архитектурная форма)',
    'Часть здания',
    "Другое",

]
header_commerce = [
    "Ссылка",
    "Площадь",
    "Адрес",
    "Тип недвижимости",
    "Дата обновления",
    "Цена, $",
    "Цена за метр, $",
    "Цена, сумм",
    "Цена за метр, сумм",
    "Описание",
    "Категория",
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
                 type_of_commerce='',
                 category="Продажа",
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
                         is_active=is_active,
                         category=category
                         )
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
            self.description,
            self.category,
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
            "is_active": self.is_active,
            "category_type": self.category
        }

    def __str__(self):
        return self.__dict__
