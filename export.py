import datetime
import os
import sys


from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from openpyxl.reader.excel import load_workbook


def read_excel_template(throw_exception, template_path="_internal/input/template.xlsm"):
    if os.path.exists(template_path):
        book = load_workbook(template_path, keep_vba=True)
        return book
    else:
        throw_exception.emit("Повреждена файловая система! Обратитесь в поддержку")


def fill_table_pyqt(table, header, data, currency, data_start=0, data_finish=100):
    table.setColumnCount(len(header))
    data = data[data_start:data_finish]
    table.setRowCount(len(data))
    table.setHorizontalHeaderLabels(header)

    fill_table_data_pyqt(table, data)
    table.resizeColumnsToContents()
    # table = QtWidgets.QTableWidget()
    if currency == 'uye':
        table.setColumnHidden(8, False)
        table.setColumnHidden(9, False)
        table.setColumnHidden(10, True)
        table.setColumnHidden(11, True)
    else:
        table.setColumnHidden(11, False)
        table.setColumnHidden(10, False)
        table.setColumnHidden(8, True)
        table.setColumnHidden(9, True)


def fill_table_data_pyqt(table, data):
    for one_row in data:
        _one_row = one_row.prepare_to_list()
        # print(_one_row)
        for i in range(len(_one_row)):
            if _one_row[i] is None:
                item = QtWidgets.QTableWidgetItem("-")
            else:
                val = str(_one_row[i])
                item = QtWidgets.QTableWidgetItem(val)
            # item.setFlags(Qt.ItemFlag.ItemIsEditable)
            table.setItem(data.index(one_row), i, item)
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable)



def fill_filtered_data(sheet, results, throw_info, name):
    if len(results) == 0:
        throw_info.emit(f"Не найдены данные по запросу для {name}")
        return
    for i in range(0, len(results)):
        sheet.append(results[i].prepare_to_list())


class Exporter(QThread):
    throw_exception = pyqtSignal(str)
    throw_info = pyqtSignal(str)
    block_closing = pyqtSignal(bool)

    def __init__(self, name, path='output/',  results=None):
        super().__init__()
        self.path = path
        self.name = name
        self.results = results
        log_out = open('_internal/output/log_out.txt', 'a', encoding="utf-8")
        log_err = open('_internal/output/log_err.txt', 'a', encoding="utf-8")
        sys.stdout = log_out
        sys.stderr = log_err

    def run(self):
        self.block_closing.emit(True)
        if not os.path.exists("output"):
            os.mkdir("output")
        self.name = f"{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}_{self.name}"
        book = read_excel_template(self.throw_exception)
        sheet = book[book.sheetnames[0]]
        sheet.title = f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}"
        fill_filtered_data(sheet=sheet,
                           results=self.results,
                           throw_info=self.throw_info,
                           name=self.name)
        self.path += f'{self.name}.xlsm'
        if os.path.exists(self.path):
            os.remove(self.path)
        book.save(self.path)
        self.block_closing.emit(False)

