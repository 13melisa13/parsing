import datetime
import os
import time
import openpyxl
from olx_parsing import fill_sheet_olx
from uybor_api import fill_sheet_uybor
import locale


locale.setlocale(locale.LC_TIME, 'ru_RU')

def read_excel_template():

    if os.path.exists(f"input/template.xlt"):

        read_teplate = xlrd.open_workbook("input/template.xlt", formatting_info=True)
        book = copy(read_teplate)
        new_excel_sheet = deepcopy(book.get_sheet(0))
        new_excel_sheet.set_name(f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}")
        book = xlwt.Workbook()
        book._Workbook__worksheets = [new_excel_sheet]
        print("by_template")

    else:
        book = xlwt.Workbook()
        book.add_sheet(f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}")
    return book


def excel_file(name_of_file, fill_sheet):
    book = read_excel_template()
    fill_sheet(book.get_sheet(0))
    if os.path.exists(f"output/{name_of_file}.xls"):
        os.remove(f"output/{name_of_file}.xls")
    book.save(f"output/{name_of_file}.xls")


def create_filtered_excel_file(fill_sheet, name):
    name += f"_{datetime.datetime.now().strftime('%d%m%y_%H%M')}"
    excel_file(
        f"output/{name}",
        fill_sheet=fill_sheet
    )


if __name__ == "__main__":
    if not os.path.exists("output/"):
        os.mkdir("output")
    start = time.time()
    excel_file("uybor", fill_sheet_uybor)
    print(time.time() - start)
    start = time.time()
    # excel_file("olx", fill_sheet_olx)
    print(time.time() - start)
