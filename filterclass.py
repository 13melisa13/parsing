import datetime
import os

from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, Qt

from filtr_excel import fill_filtered_data
from main import read_excel_template


def fill_table_pyqt(table, header, data, currency):
    table.setColumnCount(len(header))
    table.setRowCount(len(data))
    # print(header[12])
    table.setHorizontalHeaderLabels(header)
    fill_table_data_pyqt(table, data)
    table.resizeColumnsToContents()
    table.setColumnHidden(12, True)
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
        # print(len(_one_row))
        for one in _one_row:
            item = QtWidgets.QTableWidgetItem(str(one))
            if one is None:
                # print("None")
                item = QtWidgets.QTableWidgetItem("-")
            item.setFlags(Qt.ItemFlag.ItemIsSelectable)
            table.setItem(data.index(one_row), _one_row.index(one), item)


# class Filter(QThread):
#     def __init__(self, main_window):
#         super().__init__()
#         self.main_window = main_window
#
#     def run(self):
        # self.main_window.filter_button.setDisabled(True)
        # self.main_window.filter_button.setCheckable(False)
        #
        # # print(self.filters)
        # self.main_window.label_progress_bar.setText("Процесс: Фильтрация")
        # self.main_window.progress_bar.setProperty("value", 0)
        # if (not os.path.exists("_internal/output/internal/olx.xlsm") or
        #         not os.path.exists("_internal/output/internal/uybor.xlsm")):
        #     if (not os.path.exists("_internal/output/internal/olx.xlsm")
        #             and not os.path.exists("_internal/output/internal/uybor.xlsm")):
        #         self.main_window.message.setText("Необходимо загрузить данные с UyBor и Olx")
        #     elif not os.path.exists("_internal/output/internal/uybor.xlsm"):
        #         self.main_window.message.setText("Необходимо загрузить данные с UyBor")
        #     else:
        #         self.main_window.message.setText("Необходимо загрузить данные с Olx")
        #     self.main_window.message.setIcon(QMessageBox.Icon.Information)
        #     self.main_window.message.exec()
        #     return
        # else:
        # self.main_window.message.setText("Необходимо загрузить данные с Olx")
        # self.main_window.message.setIcon(QMessageBox.Icon.Information)
        # self.main_window.message.exec()
        # self.main_window.results_olx = filtration(filters=self.main_window.filters, resource="_internal/output/internal/olx.xlsm")
        #
        # self.main_window.label_rows_count_olx.setText(f"Всего строк: {len(self.main_window.results_olx)}")
        # if 'uzs' in self.main_window.filters:
        #     cur = 'uzs'
        # else:
        #     cur = 'uye'
        # fill_table_pyqt(self.main_window.table_widget_olx, header, self.main_window.results_olx, cur)
        # self.main_window.results_uybor = filtration(filters=self.main_window.filters, resource="_internal/output/internal/uybor.xlsm")
        # self.main_window.label_rows_count_uybor.setText(f"Всего строк: {len(self.main_window.results_uybor)}")

        # fill_table_pyqt(self.main_window.table_widget_uybor, header, self.main_window.results_uybor, cur)

        # self.main_window.export_button.setEnabled(len(self.main_window.results_uybor)
        #                                             + len(self.main_window.results_olx) > 0)
        #
        # self.main_window.progress_bar.setProperty("value", 100)
        # time.sleep(10)
        # print(len(self.results_uybor), len(self.results_olx))
        # self.main_window.label_progress_bar.setText("Процесс: Фильтрация - Завершено")


class Exporter(QThread):
    def __init__(self, name, path='output/', main_window=None, results=None):
        super().__init__()
        self.path = path
        self.main_window = main_window
        self.name = name
        self.results = results

    def run(self):
        if not os.path.exists("output"):
            os.mkdir("output")
        name = self.name
        if name == "Uybor":
            self.main_window.export_button_uybor.setCheckable(False)
            self.main_window.export_button_uybor.setDisabled(True)
        else:
            self.main_window.export_button_olx.setCheckable(False)
            self.main_window.export_button_olx.setDisabled(True)
        self.main_window.export_button_all_data.setCheckable(False)
        self.main_window.export_button_all_data.setDisabled(True)
        self.name += f"_{datetime.datetime.now().strftime('%d%m%y_%H%M')}"
        # self.main_window.label_progress_bar.setText(f"Процесс: Экспорт  в {self.name}.xlsm")
        book = read_excel_template(self.main_window)
        sheet = book[book.sheetnames[0]]
        start = 0
        sheet.title = f"{datetime.datetime.now().strftime('%d.%m.%y_%H.%M')}"
        fill_filtered_data(sheet=sheet, results=self.results,
                           progress=self.main_window.progress_bar,
                           start=start, main_window=self.main_window,
                           name=self.name)
        self.path += f'{self.name}.xlsm'
        if os.path.exists(self.path):
            os.remove(self.path)
        book.save(self.path)
        # self.main_window.label_progress_bar.setText("Процесс: Обновление UyBor - Завершено")
        self.main_window.progress_bar.setProperty("value", 100)

        if name == "Uybor":
            # print(self.name + "1")
            self.main_window.export_button_uybor.setCheckable(True)
            self.main_window.export_button_uybor.setEnabled(True)
        else:
            # print(self.name + "2")
            self.main_window.export_button_olx.setCheckable(not False)
            self.main_window.export_button_olx.setDisabled(not True)
        if (self.main_window.export_button_olx.isEnabled() and
                self.main_window.export_button_uybor.isEnabled()):
            self.main_window.export_button_all_data.setCheckable(not False)
            self.main_window.export_button_all_data.setDisabled(not True)
