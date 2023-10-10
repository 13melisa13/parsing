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
        print("No template file")
    return book


def create_internal_excel_file(name_of_file, fill_sheet, progress, path='output/internal/',args=[]):
    book = read_excel_template()
    sheet = book[book.sheetnames[0]]
    sheet.title = f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}"
    fill_sheet(sheet, progress, args)
    path += f'{name_of_file}.xlsm'
    if os.path.exists(path):
        os.remove(path)
    book.save(path)


def create_filtered_excel_file(fill_sheet, name,  results,  progress, start=0, path='output/'):
    name += f"_{datetime.datetime.now().strftime('%d%m%y_%H%M')}"
    if fill_sheet is None:
        return
    book = read_excel_template()
    sheet = book[book.sheetnames[0]]
    sheet.title = f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}"
    fill_sheet(sheet=sheet, results=results, progress=progress, start=start)
    path += f'{name}.xlsm'
    if os.path.exists(path):
        os.remove(path)
    book.save(path)

