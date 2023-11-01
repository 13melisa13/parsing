import datetime
import locale
import os
from openpyxl.reader.excel import load_workbook

locale.setlocale(locale.LC_TIME, 'ru_RU')


def read_excel_template(throw_exception, template_path="_internal/input/template.xlsm"):
    if os.path.exists(template_path):
        book = load_workbook(template_path, keep_vba=True)
    else:
        throw_exception.emit("Повреждена файловая система! Обратитесь в поддержку")
    return book




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
                 id=0):
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
        self.id = id

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
            self.description,
            self.id
        ]






