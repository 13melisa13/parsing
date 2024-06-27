from datetime import datetime
from models.real_estate import RealEstate

header_land = [
    "Ссылка",
    "Площадь",
    "Адрес",
    "Тип недвижимости",
    'Особенности расположения',
    "Дата обновления",
    "Цена, $",
    "Цена за метр, $",
    "Цена, сумм",
    "Цена за метр, сумм",
    "Описание",
    "Категория"
]

LAND_TYPE_CHOICES = [
    "Назначение",
    "Земля под строительство",
    "Земля под сад/огород",
    "Земля с/х назначения",
    "Земля промышленного назначения",
    "Другое",

]

LAND_LOCATION_CHOICES = [
    "Расположение",
    "В городе",
    "В пригороде",
    "В сельской местности",
    "Вдоль трассы",
    "Возле водоема, реки",
    "В предгорьях",
    "В дачном массиве",
    'На закрытой территории',

]


class Land(RealEstate):
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
                 location_feature='',
                 type_of_land='',
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
        self.location_feature = location_feature
        self.type_of_land = type_of_land

    def prepare_to_list(self):
        return [
            self.url.__str__(),
            self.square.__str__(),
            self.address.__str__(),
            self.location_feature,
            self.type_of_land,
            self.modified.__str__(),
            self.price_uye.__str__(),
            self.price_per_meter_uye.__str__(),
            self.price_uzs,
            self.price_per_meter_uzs.__str__(),
            self.description,
            self.category.__str__(),

        ]

    def prepare_to_dict(self):
        return {
            "url": self.url,
            "square": self.square,
            "address": self.address,
            "location_feature": self.location_feature,
            "type_of_land": self.type_of_land,
            "modified": self.modified.__str__(),
            "price_uye": self.price_uye,
            "price_uzs": self.price_uzs,
            "description": self.description,
            "external_id": self.external_id,
            "domain": self.domain,
            "is_active": self.is_active,
            "category": self.category.__str__(),
        }

    def __str__(self):
        return self.__dict__
