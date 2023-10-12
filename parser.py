# Form implementation generated from reading ui file 'parser.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.
import faulthandler
import os
import sys
import time

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QMessageBox

from filterclass import Filter, Exporter, fill_table_pyqt
from filtr_excel import filtration
from olx_parsing import OlxParser
from uybor_api import CURRENCY_CHOISES, REPAIR_CHOICES_UYBOR, ApiParser, header


class UiParser(QtWidgets.QMainWindow):
    results_olx = []
    results_uybor = []
    filters = {}

    def __init__(self):
        super().__init__()
        self.thread_filter = None
        self.thread_export_uybor = None
        self.thread_export_olx = None
        self.thread_uybor = None
        self.thread_olx = None
        self.setWindowTitle("MAEParser")
        # block main
        self.main_widget = QtWidgets.QWidget()
        page_layout = QtWidgets.QVBoxLayout()
        self.message = QMessageBox(self)
        self.message.setWindowTitle("MAEParser")
        # block buttons upload
        self.main_functions_layout = QtWidgets.QHBoxLayout()
        self.update_olx = QtWidgets.QPushButton("Обновить Olx")
        self.update_uybor = QtWidgets.QPushButton("Обновить UyBor")
        self.update_all_data = QtWidgets.QPushButton("Обновить Olx и UyBor")
        self.export_button = QtWidgets.QPushButton("Экспорт excel")
        self.main_functions_layout.addWidget(self.update_uybor)
        self.main_functions_layout.addWidget(self.update_olx)
        self.main_functions_layout.addWidget(self.update_all_data)
        self.main_functions_layout.addWidget(self.export_button)
        page_layout.addLayout(self.main_functions_layout)
        # block progress_bar
        self.progress_bar_layout = QtWidgets.QVBoxLayout()
        self.label_progress_bar = QtWidgets.QLabel("Выполнение текущего процесса:")
        self.progress_bar_layout.addWidget(self.label_progress_bar, 0)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar_layout.addWidget(self.progress_bar, 0)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar_layout.addSpacing(10)
        self.progress_bar_layout.addStretch(1)
        page_layout.addLayout(self.progress_bar_layout)
        # # block filters
        self.filter_layout = QtWidgets.QGridLayout()
        # # labels - first line
        self.label_price = QtWidgets.QLabel("Цена")
        self.label_square = QtWidgets.QLabel("Площадь")
        self.label_floor = QtWidgets.QLabel("Этаж")
        self.label_total_floor = QtWidgets.QLabel("Этажность")
        self.filter_button = QtWidgets.QPushButton("Отфильтровать")

        self.filter_layout.addWidget(self.label_price, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.label_square, 0, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.label_floor, 0, 5, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.label_total_floor, 0, 7, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.filter_button, 2, 9, 1, 2, Qt.AlignmentFlag.AlignCenter)
        # inputs second line
        self.price_min = QtWidgets.QLineEdit()
        self.price_min.setPlaceholderText("min")
        self.price_min.setValidator(QIntValidator(1, 999999999, self))
        self.price_max = QtWidgets.QLineEdit()
        self.price_max.setPlaceholderText("max")
        self.price_max.setValidator(QIntValidator(1, 999999999, self))
        self.currency_type = QtWidgets.QComboBox()
        self.square_min = QtWidgets.QLineEdit()
        self.square_max = QtWidgets.QLineEdit()
        self.floor_min = QtWidgets.QLineEdit()
        self.floor_max = QtWidgets.QLineEdit()
        self.total_floor_min = QtWidgets.QLineEdit()
        self.total_floor_max = QtWidgets.QLineEdit()
        self.square_max.setValidator(QIntValidator(1, 10000, self))
        self.square_min.setValidator(QIntValidator(1, 10000, self))
        self.floor_max.setValidator(QIntValidator(1, 200, self))
        self.floor_min.setValidator(QIntValidator(1, 200, self))
        self.total_floor_max.setValidator(QIntValidator(1, 200, self))
        self.total_floor_min.setValidator(QIntValidator(1, 200, self))
        self.square_max.setPlaceholderText("max")
        self.floor_max.setPlaceholderText("max")
        self.total_floor_max.setPlaceholderText("max")
        self.total_floor_min.setPlaceholderText("min")
        self.square_min.setPlaceholderText("min")
        self.floor_min.setPlaceholderText("min")

        self.filter_layout.addWidget(self.price_min, 2, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.price_max, 2, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.filter_layout.addWidget(self.square_min, 2, 3, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.square_max, 2, 4, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.floor_min, 2, 5, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.floor_max, 2, 6, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.total_floor_min, 2, 7, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.total_floor_max, 2, 8, 1, 1, Qt.AlignmentFlag.AlignCenter)
        # self.threads = []
        # combo_boxs on second line
        self.room_type = QtWidgets.QComboBox()
        self.repair_type = QtWidgets.QComboBox()
        self.is_new_building_type = QtWidgets.QComboBox()
        self.label_cur = QtWidgets.QLabel("Валюта")
        self.filter_layout.addWidget(self.label_cur, 3, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.currency_type, 3, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.is_new_building_type, 3, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.repair_type, 3, 5, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.room_type, 3, 7, 1, 2, Qt.AlignmentFlag.AlignCenter)
        page_layout.addLayout(self.filter_layout)
        self.filters.update({"uzs": True})
        # endblock filters
        # block preview
        self.data_view_layout = QtWidgets.QVBoxLayout()
        # self.label_preview = QtWidgets.QLabel("Предпросмотр")
        self.data_view = QtWidgets.QTabWidget()
        # self.data_view_layout.addWidget(self.label_preview)
        self.data_view_layout.addWidget(self.data_view)
        # block uybor table
        self.uybor_widget = QtWidgets.QWidget()
        self.layout_uybor = QtWidgets.QVBoxLayout()
        self.label_rows_count_uybor = QtWidgets.QLabel("Всего строк: 0")
        self.layout_uybor.addWidget(self.label_rows_count_uybor)
        self.uybor_widget.setLayout(self.layout_uybor)
        self.table_widget_uybor = QtWidgets.QTableWidget()

        self.layout_uybor.addWidget(self.table_widget_uybor)
        # block olx table
        self.olx_widget = QtWidgets.QWidget()
        self.layout_olx = QtWidgets.QVBoxLayout()
        self.label_rows_count_olx = QtWidgets.QLabel("Всего строк: 0")
        self.layout_olx.addWidget(self.label_rows_count_olx)
        self.olx_widget.setLayout(self.layout_olx)
        self.table_widget_olx = QtWidgets.QTableWidget()
        self.layout_olx.addWidget(self.table_widget_olx)
        self.data_view.addTab(self.olx_widget, "OLX")
        self.data_view.addTab(self.uybor_widget, "UyBor")
        self.data_view.setCurrentIndex(0)
        page_layout.addLayout(self.data_view_layout)
        page_layout.addSpacing(10)
        page_layout.addStretch(1)
        self.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(page_layout)
        self.setCentralWidget(self.main_widget)
        self.add_items_for_combo_box()
        self.handler()

    def add_items_for_combo_box(self):
        self.is_new_building_type.addItems(["Тип квартиры", "Новостройки", "Вторичный"])
        self.room_type.addItems(["Кол-во комнат", "Студия", "1", "2", "3", "4", "5", "6+"])
        self.currency_type.addItems(CURRENCY_CHOISES)
        self.repair_type.addItems([REPAIR_CHOICES_UYBOR[one] for one in REPAIR_CHOICES_UYBOR])

    def update_all_data_clicked(self):
        self.update_uybor_clicked()
        self.update_olx_clicked()

    def update_uybor_clicked(self):
        self.filter_button.setEnabled(True)
        self.thread_uybor = ApiParser(main_window=self)
        self.thread_uybor.finished.connect(self.thread_uybor.deleteLater)
        self.thread_uybor.start()

    def update_olx_clicked(self):
        self.filter_button.setEnabled(True)
        self.thread_olx = OlxParser(main_window=self)
        self.thread_olx.finished.connect(self.thread_olx.deleteLater)
        self.thread_olx.start()

    def filter_button_clicked(self):
        self.results_olx = filtration(filters=self.filters, resource="_internal/output/internal/olx.xlsm")
        #
        self.label_rows_count_olx.setText(f"Всего строк: {len(self.results_olx)}")
        if 'uzs' in self.filters:
            cur = 'uzs'
        else:
            cur = 'uye'
        fill_table_pyqt(self.table_widget_olx, header, self.results_olx, cur)
        self.results_uybor = filtration(filters=self.filters, resource="_internal/output/internal/uybor.xlsm")
        self.label_rows_count_uybor.setText(f"Всего строк: {len(self.results_uybor)}")
        fill_table_pyqt(self.table_widget_uybor, header, self.results_uybor, cur)
        self.export_button.setEnabled(len(self.results_uybor) + len(self.results_olx) > 0)
        self.progress_bar.setProperty("value", 100)

    def export_button_clicked(self):
        self.thread_export_uybor = Exporter(main_window=self, name="Uybor", results=self.results_uybor, )
        self.thread_export_uybor.finished.connect(self.thread_export_uybor.deleteLater)
        self.thread_export_uybor.start()
        self.thread_export_olx = Exporter(main_window=self, name="Olx", results=self.results_olx)
        self.thread_export_olx.finished.connect(self.thread_export_olx.deleteLater)
        self.thread_export_olx.start()

    def cur_chosen(self):

        self.filter_button.setEnabled(True)
        if self.currency_type.currentText() == "СУММ.":
            self.filters.update({"uzs": True})
            self.table_widget_olx.setColumnHidden(11, not False)
            self.table_widget_olx.setColumnHidden(10, not False)
            self.table_widget_olx.setColumnHidden(8, not True)
            self.table_widget_olx.setColumnHidden(9, not True)
            self.table_widget_uybor.setColumnHidden(11, not False)
            self.table_widget_uybor.setColumnHidden(10, not False)
            self.table_widget_uybor.setColumnHidden(8, not True)
            self.table_widget_uybor.setColumnHidden(9, not True)
            if "uye" in self.filters:
                self.filters.pop("uye")
        else:
            self.filters.update({"uye": True})

            self.table_widget_uybor.setColumnHidden(8, False)
            self.table_widget_uybor.setColumnHidden(9, False)
            self.table_widget_uybor.setColumnHidden(10, True)
            self.table_widget_uybor.setColumnHidden(11, True)
            self.table_widget_olx.setColumnHidden(8, False)
            self.table_widget_olx.setColumnHidden(9, False)
            self.table_widget_olx.setColumnHidden(10, True)
            self.table_widget_olx.setColumnHidden(11, True)
            if "uzs" in self.filters:
                self.filters.pop("uzs")


    def room_chosen(self):
        self.filter_button.setEnabled(True)
        if self.room_type.currentText() != "Кол-во комнат":
            self.filters.update({"room": self.room_type.currentText()})
        else:
            self.filters.pop("room")


    def is_new_building_chosen(self):
        self.filter_button.setEnabled(True)
        if self.is_new_building_type.currentText() != "Тип квартиры":
            self.filters.update({"is_new_building": self.is_new_building_type.currentText()})
        else:
            self.filters.pop("is_new_building")
        time.sleep(1)

    def repair_chosen(self):
        self.filter_button.setEnabled(True)

        if self.repair_type.currentText() != "Ремонт":
            self.filters.update({"repair": self.repair_type.currentText()})
        else:
            self.filters.pop("repair")
        time.sleep(1)

    def price_min_changed(self):
        self.filter_button.setEnabled(True)
        if self.price_min.text() != "":
            self.filters.update({"price_min": int(self.price_min.text())})
        else:
            self.filters.pop("price_min")

    def price_max_changed(self):
        self.filter_button.setEnabled(True)
        if self.price_max.text() != "":
            self.filters.update({"price_max": int(self.price_max.text())})
        else:
            self.filters.pop("price_max")

    def floor_min_changed(self):
        self.filter_button.setCheckable(True)
        if self.floor_min.text() != "":
            self.filters.update({"floor_min": int(self.floor_min.text())})
        else:
            self.filters.pop("floor_min")

    def floor_max_changed(self):
        self.filter_button.setEnabled(True)
        if self.floor_max.text() != "":
            self.filters.update({"floor_max": int(self.floor_max.text())})
        else:
            self.filters.pop("floor_max")

    def square_min_changed(self):
        self.filter_button.setEnabled(True)

        if self.square_min.text() != "":
            self.filters.update({"square_min": float(self.square_min.text())})
        else:
            self.filters.pop("square_min")

    def square_max_changed(self):
        self.filter_button.setEnabled(True)

        if self.square_max.text() != "":
            self.filters.update({"square_max": float(self.square_max.text())})
        else:
            self.filters.pop("square_max")

    def total_floor_min_changed(self):
        self.filter_button.setEnabled(True)

        if self.total_floor_min.text() != "":
            self.filters.update({"total_floor_min": int(self.total_floor_min.text())})
        else:
            self.filters.pop("total_floor_min")

    def total_floor_max_changed(self):
        self.filter_button.setEnabled(True)

        if self.total_floor_max.text() != "":
            self.filters.update({"total_floor_max": int(self.total_floor_max.text())})
        else:
            self.filters.pop("total_floor_max")

    def handler(self):
        self.room_type.activated.connect(self.room_chosen)
        self.repair_type.activated.connect(self.repair_chosen)
        self.currency_type.activated.connect(self.cur_chosen)
        self.is_new_building_type.activated.connect(self.is_new_building_chosen)
        self.export_button.setCheckable(True)
        if len(self.results_uybor) + len(self.results_olx) < 0:
            self.export_button.setDisabled(True)
        else:
            self.export_button.setDisabled(False)

        self.export_button.clicked.connect(self.export_button_clicked)
        self.update_all_data.setCheckable(True)
        self.update_all_data.clicked.connect(self.update_all_data_clicked)
        self.update_olx.setCheckable(True)

        self.update_olx.clicked.connect(self.update_olx_clicked)
        self.update_uybor.setCheckable(True)
        self.update_uybor.clicked.connect(self.update_uybor_clicked)
        self.filter_button.setCheckable(True)
        self.filter_button.clicked.connect(self.filter_button_clicked)
        self.price_min.textChanged.connect(self.price_min_changed)
        self.price_max.textChanged.connect(self.price_max_changed)
        self.square_min.textChanged.connect(self.square_min_changed)
        self.square_max.textChanged.connect(self.square_max_changed)
        self.floor_min.textChanged.connect(self.floor_min_changed)
        self.floor_max.textChanged.connect(self.floor_max_changed)
        self.total_floor_max.textChanged.connect(self.total_floor_max_changed)
        self.total_floor_min.textChanged.connect(self.total_floor_min_changed)

    def show(self):
        super().show()
        self.filter_button_clicked()


if __name__ == "__main__":
    faulthandler.enable()
    if not os.path.exists("_internal/output"):
        os.mkdir("_internal/output")
    if not os.path.exists("_internal/output/internal"):
        os.mkdir("_internal/output/internal")
    app = QtWidgets.QApplication(sys.argv)
    ui = UiParser()
    ui.show()
    sys.exit(app.exec())
