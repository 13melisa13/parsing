import datetime
import os
import time
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from filtr_excel import fill_filtered_data
from olx_parsing import fill_sheet_olx
from uybor_api import fill_sheet_uybor
import locale


locale.setlocale(locale.LC_TIME, 'ru_RU')


def read_excel_template(template_path="input/template.xlsm"):
    if os.path.exists(template_path):
        book = load_workbook(template_path, keep_vba=True)
    else:
        book = Workbook()
    return book


def create_internal_excel_file(name_of_file, fill_sheet, args=[]):
    book = read_excel_template()
    sheet = book[book.sheetnames[0]]
    sheet.title = f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}"
    fill_sheet(sheet, args)
    if os.path.exists(f"output/{name_of_file}.xlsm"):
        os.remove(f"output/{name_of_file}.xlsm")
    book.save(f"output/{name_of_file}.xlsm")


def create_filtered_excel_file(fill_sheet, name, filters):
    name += f"_{datetime.datetime.now().strftime('%d%m%y_%H%M')}"
    if fill_sheet is None:
        return
    create_internal_excel_file(
        name,
        fill_sheet=fill_sheet,
        args=filters   # TODO input = dict()
    )


if __name__ == "__main__":
    if not os.path.exists("output/"):
        os.mkdir("output")
    start = time.time()
    create_internal_excel_file("uybor", fill_sheet_uybor)
    print(time.time() - start)
    start = time.time()
    create_internal_excel_file("olx", fill_sheet_olx)
    print(time.time() - start)
    create_filtered_excel_file(fill_filtered_data,
                               "uybor",
                               {
                                   "resource": "output/uybor.xlsm",
                                   "room": "3",
                                   "repair": "Евроремонт",
                                   "is_new_building": "Вторичный",
                                   "square_max": 76,
                                   "square_min": 70,

                                })
# TODO получать количество элементов списка и потом кнопка выгрузки