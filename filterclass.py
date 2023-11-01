import datetime
import os
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from olx_parsing import fill_filtered_data
from main import read_excel_template


def fill_table_pyqt(table, header, data, currency):
    table.setColumnCount(len(header))
    table.setRowCount(len(data))
    # print(header[12])
    table.setHorizontalHeaderLabels(header)
    fill_table_data_pyqt(table, data)
    table.resizeColumnsToContents()
    table = QtWidgets.QTableWidget()
    # table.setColumnHidden(12, True)
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
        for one in _one_row:
            item = QtWidgets.QTableWidgetItem(str(one))
            if one is None:
                item = QtWidgets.QTableWidgetItem("-")
            item.setFlags(Qt.ItemFlag.ItemIsSelectable)
            table.setItem(data.index(one_row), _one_row.index(one), item)


class Exporter(QThread):
    throw_exception = pyqtSignal(str)
    throw_info = pyqtSignal(str)
    block_closing = pyqtSignal(bool)

    def __init__(self, name, path='output/',  results=None):
        super().__init__()
        self.path = path
        self.name = name
        self.results = results

    def run(self):
        self.block_closing.emit(True)
        if not os.path.exists("output"):
            os.mkdir("output")
        self.name = f"{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}_{self.name}"
        book = read_excel_template(self.throw_exception)
        sheet = book[book.sheetnames[0]]
        sheet.title = f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}"
        fill_filtered_data(sheet=sheet, results=self.results, throw_info=self.throw_info,
                           name=self.name)
        self.path += f'{self.name}.xlsm'
        if os.path.exists(self.path):
            os.remove(self.path)
        book.save(self.path)
        self.block_closing.emit(False)

