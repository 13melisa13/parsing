import datetime
import os
import sys

from PyQt6 import QtGui
from PyQt6.QtWidgets import QMessageBox

from PyQt6 import QtCore
from openpyxl.reader.excel import load_workbook

import locale


locale.setlocale(locale.LC_TIME, 'ru_RU')


def read_excel_template(main_window, template_path="_internal/input/template.xlsm"):
    if os.path.exists(template_path):
        book = load_workbook(template_path, keep_vba=True)
    else:
        main_window.message.setText(f"Повреждена файловая система! Обратитесь в поддержку")
        main_window.message.setIcon(QMessageBox.Icon.Critical)
        main_window.message.exec()
        sys.exit()
    return book


def create_internal_excel_file(name_of_file, fill_sheet, progress, path='_internal/output/internal/',args=[], main_window=None):
    book = read_excel_template(main_window)
    sheet = book[book.sheetnames[0]]
    sheet.title = f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}"
    if not os.path.exists(path):
        main_window.message.setText(f"Повреждена файловая система! Перезагрузите приложение")
        main_window.message.setIcon(QMessageBox.Icon.Critical)
        main_window.message.exec()
        sys.exit()
        # palette = QtGui.QPalette(progress.palette())
        # palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(QtCore.Qt.GlobalColor.red))
        # progress.setPalette(palette)
        # return
    fill_sheet(sheet, progress, args)
    path += f'{name_of_file}.xlsm'
    if os.path.exists(path):
        os.remove(path)
    book.save(path)


def create_filtered_excel_file(fill_sheet, name,  results,  progress, start=0, path='_internal/output/', main_window=None):
    name += f"_{datetime.datetime.now().strftime('%d%m%y_%H%M')}"
    if fill_sheet is None:
        return
    book = read_excel_template(main_window)
    sheet = book[book.sheetnames[0]]
    sheet.title = f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}"
    fill_sheet(sheet=sheet, results=results, progress=progress, start=start, main_window=main_window, name=name)
    path += f'{name}.xlsm'
    if os.path.exists(path):
        os.remove(path)
    book.save(path)

