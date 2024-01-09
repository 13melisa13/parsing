from datetime import datetime

CURRENCY_CHOISES = [
    "СУММ.", "У.Е."
]


class RealEstate:
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
                 is_active=True):
        try:
            self.price_uye = float(price_uye)
            self.price_per_meter_uye = "%.2f" % (float(price_uye) / float(square))
        except Exception:
            self.price_uye = 0
            self.price_per_meter_uye = 'default'
        try:
            self.price_uzs = float(price_uzs)
            self.price_per_meter_uzs = "%.2f" % (float(price_uzs) / float(square))
        except Exception:
            self.price_uzs = 0
            self.price_per_meter_uzs = 'default'
        self.square = float(square.__str__().replace(" ", ''))
        self.description = description
        self.address = address
        try:
            date_time = datetime.fromisoformat(modified)
        except ValueError:
            date_time = datetime.strptime(modified, "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as ex:
            # print('blyat modified', modified, type(ex))
            date_time = datetime.now()
        self.modified = date_time
        self.url = url
        self.external_id = id
        self.domain = domain
        self.is_active = is_active

    def prepare_to_list(self):
        return [
            self.url.__str__(),
            self.square.__str__(),
            # f'{self.floor}/{self.total_floor}',
            self.address.__str__(),
            # self.repair.__str__(),
            # self.is_new_building.__str__(),
            # self.room.__str__(),
            self.modified.__str__(),
            self.price_uye.__str__(),
            self.price_per_meter_uye.__str__(),
            self.price_uzs,
            self.price_per_meter_uzs.__str__(),
            self.description
        ]

    def prepare_to_dict(self):
        return {
            "url": self.url,
            "square": self.square,
            # "floor": self.floor,
            # "total_floor": self.total_floor,
            "address": self.address,
            # "repair": self.repair,
            # "is_new_building": self.is_new_building,
            # "room": self.room,
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
