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







