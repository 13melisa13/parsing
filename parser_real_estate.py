import datetime
import json
import os
import re
import sys
import time
from urllib.request import urlopen

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QTime, QTimer, QDateTime, QTimeZone
from PyQt6.QtGui import QIntValidator, QCursor, QIcon
from PyQt6.QtWidgets import QMessageBox
from bs4 import BeautifulSoup

from export import Exporter, fill_table_pyqt
from models.commerce import COMMERCE_CHOICES, header_commerce
from models.flat import header_flat, REPAIR_CHOICES_UYBOR
from models.land import LAND_LOCATION_CHOICES, LAND_TYPE_CHOICES, header_land
from models.real_estate import CURRENCY_CHOICES, CATEGORY_CHOICES
from getter_from_db import DataFromDB
from filtration import filtration
import pytz

from upload_olx import UploadOlx

tz = pytz.timezone('Asia/Tashkent')


def get_rate():
    url = 'https://ofb.uz/uz/'
    while True:
        try:
            page = urlopen(url)
            html = page.read().decode('utf-8')
            soup = BeautifulSoup(html, "html.parser")
            curs = soup.find_all(name="div", attrs={"class": "currency"})
            return float(re.search(r"(\d+)\.(\d+)", curs[0].get_text())[0])
        except Exception as arr:
            print(arr, url, "rate")
            time.sleep(1)
            continue


class UiParser(QtWidgets.QMainWindow):
    results_olx_flat = []

    results_olx_flat_filtered = []
    results_olx_land = []
    results_olx_land_filtered = []
    results_olx_commerce = []
    results_olx_commerce_filtered = []
    filters = [{"uzs": True}, {"uzs": True}, {"uzs": True}]

    def __init__(self, json_data=None):
        super().__init__()
        # разрешение на закрытие окна todo проверить
        self.can_be_closed = [True for i in range(12)]
        self.rate = get_rate()
        self.s_ = 0
        self.f_ = 100
        print(f"time start app {datetime.datetime.now(tz=tz)}")
        # модуль установки времени обновления
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.time_update)
        self.set_time_label = QtWidgets.QLabel("Время обновления: ")
        self.set_time_button = QtWidgets.QPushButton("Настроить время обновления")
        self.set_time_label_time = QtWidgets.QLabel("Не выбрано")

        # получение данных из дампа о времени обновления
        # если данных нет, то устанавливаем пустое время
        if json_data is None or json_data["time_fixed"]["h"] == -1:
            self.time_fixed = QTime()
            self.set_time_input = QtWidgets.QTimeEdit()
        else:
            self.time_fixed = QTime(json_data["time_fixed"]["h"],
                                    json_data["time_fixed"]["m"], 0, 0)
            self.time_temp = self.time_fixed
            self.time_clicked()
            self.set_time_input = QtWidgets.QTimeEdit(self.time_fixed)
            self.set_time_label_time = QtWidgets.QLabel(f"Каждый день в {self.time_fixed.toString()}")

        # главные настройки окна
        self.setWindowTitle("MAEParser")
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.message = QMessageBox(self)
        self.message.setWindowTitle("MAEParser")
        self.message.setWindowIcon(QIcon('_internal/input/icon.ico'))

        # слой для настройки времени обновления
        self.set_time_layout = QtWidgets.QHBoxLayout()
        self.set_time_layout.addWidget(self.set_time_label)
        self.set_time_layout.addWidget(self.set_time_label_time)
        self.set_time_layout.addWidget(self.set_time_input)
        self.set_time_layout.addWidget(self.set_time_button)
        self.main_layout.addLayout(self.set_time_layout)
        # слой для вкладок
        self.data_view_layout = QtWidgets.QVBoxLayout()
        self.data_view = QtWidgets.QTabWidget()
        self.data_view_layout.addWidget(self.data_view)

        # слой страницы квартир
        self.flat_widget = QtWidgets.QWidget()
        page_flat = QtWidgets.QVBoxLayout()
        page_flat = self.page_flat_set(page_flat, json_data)
        self.flat_widget.setLayout(page_flat)
        # слой страницы участков
        self.land_widget = QtWidgets.QWidget()
        page_land = QtWidgets.QVBoxLayout()
        page_land = self.page_land_set(page_land, json_data)
        self.land_widget.setLayout(page_land)
        # слой страницы коммерции
        self.commerce_widget = QtWidgets.QWidget()
        page_commerce = QtWidgets.QVBoxLayout()
        page_commerce = self.page_commerce_set(page_commerce, json_data)
        self.commerce_widget.setLayout(page_commerce)
        # добавление вкладок и установка первой вкладки
        self.data_view.addTab(self.flat_widget, "Квартиры")
        self.data_view.addTab(self.commerce_widget, "Коммерция")
        self.data_view.addTab(self.land_widget, "Участки")
        self.data_view.setCurrentIndex(0)
        self.data_view_layout.setStretchFactor(page_flat, 1)
        # добавление слоя в главный слой
        self.main_layout.addLayout(self.data_view_layout)
        self.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        # настройка окон фильтров
        self.add_items_for_combo_box()
        # настройка кнопок
        self.handler()

    def page_flat_set(self, page_flat, json_data=None):
        if json_data is not None and json_data["time_last_olx_flat"]["h"] != -1:
            self.time_last_olx_flat = QDateTime(
                json_data["time_last_olx_flat"]["y"],
                json_data["time_last_olx_flat"]["M"],
                json_data["time_last_olx_flat"]["d"],
                json_data["time_last_olx_flat"]["h"],
                json_data["time_last_olx_flat"]["m"],
                0, 0)
            self.label_progress_bar_olx_flat = QtWidgets.QLabel(
                f"Последнее обновление квартир {self.time_last_olx_flat.toString()}")
        else:
            self.time_last_olx_flat = QDateTime()
            self.label_progress_bar_olx_flat = QtWidgets.QLabel("Данные квартир не загружены")

        self.update_layout_flat = QtWidgets.QHBoxLayout()
        self.update_olx_flat = QtWidgets.QPushButton("Обновить квартиры")
        self.export_button_olx_flat = QtWidgets.QPushButton("Экспорт в excel")

        self.update_layout_flat.addWidget(self.update_olx_flat)
        self.export_layout_flat = QtWidgets.QHBoxLayout()
        self.export_layout_flat.addWidget(self.export_button_olx_flat)

        page_flat.addLayout(self.export_layout_flat)
        page_flat.addLayout(self.update_layout_flat)

        self.progress_bar_layout_flat = QtWidgets.QVBoxLayout()

        self.progress_bar_layout_flat.addWidget(self.label_progress_bar_olx_flat, 0)
        self.progress_bar_olx_flat = QtWidgets.QProgressBar()
        self.progress_bar_layout_flat.addWidget(self.progress_bar_olx_flat, 0)
        self.progress_bar_olx_flat.setProperty("value", 0)

        self.progress_bar_layout_flat.addSpacing(10)
        self.progress_bar_layout_flat.addStretch(1)
        page_flat.addLayout(self.progress_bar_layout_flat)
        # # block filters
        self.filter_layout_flat = QtWidgets.QGridLayout()
        # # labels - first line
        self.label_category_flat = QtWidgets.QLabel("Категория")

        self.label_price_flat = QtWidgets.QLabel("Цена")
        self.label_square_flat = QtWidgets.QLabel("Площадь")
        self.label_floor_flat = QtWidgets.QLabel("Этаж")
        self.label_total_floor_flat = QtWidgets.QLabel("Этажность")
        self.filter_button_flat = QtWidgets.QPushButton("Отфильтровать")

        self.filter_layout_flat.addWidget(self.label_category_flat, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.label_price_flat, 0, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.label_square_flat, 0, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.label_floor_flat, 0, 5, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.label_total_floor_flat, 0, 7, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # inputs second line
        self.category_flat = QtWidgets.QComboBox()

        self.price_min_flat = QtWidgets.QLineEdit()
        self.price_min_flat.setPlaceholderText("min")
        self.price_min_flat.setValidator(QIntValidator(1, 999999999, self))
        self.price_max_flat = QtWidgets.QLineEdit()
        self.price_max_flat.setPlaceholderText("max")
        self.price_max_flat.setValidator(QIntValidator(1, 999999999, self))
        self.currency_type_flat = QtWidgets.QComboBox()
        self.square_min_flat = QtWidgets.QLineEdit()
        self.square_max_flat = QtWidgets.QLineEdit()
        self.floor_min_flat = QtWidgets.QLineEdit()
        self.floor_max_flat = QtWidgets.QLineEdit()
        self.total_floor_min_flat = QtWidgets.QLineEdit()
        self.total_floor_max_flat = QtWidgets.QLineEdit()
        self.square_max_flat.setValidator(QIntValidator(1, 10000, self))
        self.square_min_flat.setValidator(QIntValidator(1, 10000, self))
        self.floor_max_flat.setValidator(QIntValidator(1, 200, self))
        self.floor_min_flat.setValidator(QIntValidator(1, 200, self))
        self.total_floor_max_flat.setValidator(QIntValidator(1, 200, self))
        self.total_floor_min_flat.setValidator(QIntValidator(1, 200, self))
        self.square_max_flat.setPlaceholderText("max")
        self.floor_max_flat.setPlaceholderText("max")
        self.total_floor_max_flat.setPlaceholderText("max")
        self.total_floor_min_flat.setPlaceholderText("min")
        self.square_min_flat.setPlaceholderText("min")
        self.floor_min_flat.setPlaceholderText("min")

        self.time_temp = QTime(0, 0, 0)
        self.filter_layout_flat.addWidget(self.category_flat, 2, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.price_min_flat, 2, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.price_max_flat, 2, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.square_min_flat, 2, 3, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.square_max_flat, 2, 4, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.floor_min_flat, 2, 5, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.floor_max_flat, 2, 6, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.total_floor_min_flat, 2, 7, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_flat.addWidget(self.total_floor_max_flat, 2, 8, 1, 1, Qt.AlignmentFlag.AlignCenter)

        # combo_boxs on second line
        self.room_type_flat = QtWidgets.QComboBox()
        self.repair_type_flat = QtWidgets.QComboBox()
        self.is_new_building_type_flat = QtWidgets.QComboBox()
        self.label_cur_flat = QtWidgets.QLabel("Валюта")
        self.keywords_flat = QtWidgets.QLineEdit()
        self.label_key_flat = QtWidgets.QLabel("Ключевые слова")
        self.keywords_flat.setPlaceholderText("слово1;слово2...")
        # self.time_fixed = QTime()
        self.filter_layout_1_flat = QtWidgets.QHBoxLayout()
        self.filter_layout_1_flat.addWidget(self.label_cur_flat)
        self.filter_layout_1_flat.addWidget(self.currency_type_flat)
        self.filter_layout_1_flat.addWidget(self.is_new_building_type_flat)
        self.filter_layout_1_flat.addWidget(self.repair_type_flat)
        self.filter_layout_1_flat.addWidget(self.room_type_flat)

        self.filter_layout_1_flat.addWidget(self.label_key_flat)
        self.filter_layout_1_flat.addWidget(self.keywords_flat)
        self.filter_layout_1_flat.addWidget(self.filter_button_flat)
        page_flat.addLayout(self.filter_layout_flat)
        page_flat.addLayout(self.filter_layout_1_flat)

        # endblock filters

        # block preview
        self.data_view_layout_flat = QtWidgets.QVBoxLayout()

        # block olx table
        self.olx_widget_flat = QtWidgets.QWidget()
        self.layout_olx_flat = QtWidgets.QVBoxLayout()
        self.label_rows_count_olx_flat = QtWidgets.QLabel("Всего строк: 0")
        self.layout_olx_flat.addWidget(self.label_rows_count_olx_flat)
        self.olx_widget_flat.setLayout(self.layout_olx_flat)
        self.table_widget_olx_flat = QtWidgets.QTableWidget()
        self.layout_olx_flat.addWidget(self.table_widget_olx_flat)
        self.data_view_layout_flat.addWidget(self.olx_widget_flat)

        page_flat.addLayout(self.data_view_layout_flat)
        page_flat.addSpacing(10)
        page_flat.setStretchFactor(self.data_view_layout_flat, 1)
        return page_flat

    def tab_changed(self):
        # self.filters = {"uzs": True}
        self.price_max_flat.clear()
        self.price_max_land.clear()
        self.price_max_commerce.clear()
        self.price_min_flat.clear()
        self.price_min_land.clear()
        self.price_min_commerce.clear()
        self.floor_max_flat.clear()
        self.floor_min_flat.clear()
        self.total_floor_max_flat.clear()
        self.total_floor_min_flat.clear()
        self.square_max_flat.clear()
        self.square_max_land.clear()
        self.square_max_commerce.clear()
        self.square_min_flat.clear()
        self.square_min_land.clear()
        self.square_min_commerce.clear()
        self.keywords_commerce.clear()
        self.keywords_land.clear()
        self.keywords_flat.clear()
        self.type_commerce.setCurrentIndex(0)
        self.purpose_type_land.setCurrentIndex(0)
        self.location_type_land.setCurrentIndex(0)
        self.is_new_building_type_flat.setCurrentIndex(0)
        self.room_type_flat.setCurrentIndex(0)
        self.currency_type_flat.setCurrentIndex(0)
        self.currency_type_land.setCurrentIndex(0)
        self.currency_type_commerce.setCurrentIndex(0)
        self.repair_type_flat.setCurrentIndex(0)

    def page_land_set(self, page_land, json_data=None):
        if json_data is not None and json_data["time_last_olx_land"]["h"] != -1:
            self.time_last_olx_land = QDateTime(
                json_data["time_last_olx_land"]["y"],
                json_data["time_last_olx_land"]["M"],
                json_data["time_last_olx_land"]["d"],
                json_data["time_last_olx_land"]["h"],
                json_data["time_last_olx_land"]["m"],
                0, 0)
            self.label_progress_bar_olx_land = QtWidgets.QLabel(
                f"Последнее обновление участков с {self.time_last_olx_land.toString()}")
        else:
            self.time_last_olx_land = QDateTime()
            self.label_progress_bar_olx_land = QtWidgets.QLabel("Данные участков не загружены")

        self.update_layout_land = QtWidgets.QHBoxLayout()
        self.update_olx_land = QtWidgets.QPushButton("Обновить участки")

        self.export_button_olx_land = QtWidgets.QPushButton("Экспорт в excel")

        self.update_layout_land.addWidget(self.update_olx_land)

        self.export_layout_land = QtWidgets.QHBoxLayout()
        self.export_layout_land.addWidget(self.export_button_olx_land)

        page_land.addLayout(self.export_layout_land)
        page_land.addLayout(self.update_layout_land)
        # block progress_bar

        self.progress_bar_layout_land = QtWidgets.QVBoxLayout()

        self.progress_bar_layout_land.addWidget(self.label_progress_bar_olx_land, 0)
        self.progress_bar_olx_land = QtWidgets.QProgressBar()
        self.progress_bar_layout_land.addWidget(self.progress_bar_olx_land, 0)
        self.progress_bar_olx_land.setProperty("value", 0)

        self.progress_bar_layout_land.addSpacing(10)
        self.progress_bar_layout_land.addStretch(1)
        page_land.addLayout(self.progress_bar_layout_land)
        # # block filters
        self.filter_layout_land = QtWidgets.QGridLayout()
        # # labels - first line
        self.label_category_land = QtWidgets.QLabel("Категория")
        self.label_price_land = QtWidgets.QLabel("Цена")
        self.label_square_land = QtWidgets.QLabel("Площадь")

        self.filter_button_land = QtWidgets.QPushButton("Отфильтровать")

        self.filter_layout_land.addWidget(self.label_category_land, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_land.addWidget(self.label_price_land, 0, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_land.addWidget(self.label_square_land, 0, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # inputs second line
        self.category_land = QtWidgets.QComboBox()

        self.price_min_land = QtWidgets.QLineEdit()
        self.price_min_land.setPlaceholderText("min")
        self.price_min_land.setValidator(QIntValidator(1, 999999999, self))
        self.price_max_land = QtWidgets.QLineEdit()
        self.price_max_land.setPlaceholderText("max")
        self.price_max_land.setValidator(QIntValidator(1, 999999999, self))
        self.currency_type_land = QtWidgets.QComboBox()
        self.square_min_land = QtWidgets.QLineEdit()
        self.square_max_land = QtWidgets.QLineEdit()

        self.square_max_land.setValidator(QIntValidator(1, 10000, self))
        self.square_min_land.setValidator(QIntValidator(1, 10000, self))

        self.square_max_land.setPlaceholderText("max")

        self.square_min_land.setPlaceholderText("min")
        self.time_temp = QTime(0, 0, 0)
        self.filter_layout_land.addWidget(self.category_land, 2, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_land.addWidget(self.price_min_land, 2, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_land.addWidget(self.price_max_land, 2, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_land.addWidget(self.square_min_land, 2, 3, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_land.addWidget(self.square_max_land, 2, 4, 1, 1, Qt.AlignmentFlag.AlignCenter)

        # combo_boxs on second line
        self.purpose_type_land = QtWidgets.QComboBox()
        # self.repair_type_land = QtWidgets.QComboBox()
        self.location_type_land = QtWidgets.QComboBox()
        self.label_cur_land = QtWidgets.QLabel("Валюта")
        self.keywords_land = QtWidgets.QLineEdit()
        self.label_key_land = QtWidgets.QLabel("Ключевые слова")
        self.keywords_land.setPlaceholderText("слово1;слово2...")
        # self.time_fixed = QTime()
        self.filter_layout_1_land = QtWidgets.QHBoxLayout()
        self.filter_layout_land.addWidget(self.purpose_type_land, 2, 5, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_1_land.addWidget(self.label_cur_land)
        self.filter_layout_1_land.addWidget(self.currency_type_land)
        self.filter_layout_1_land.addWidget(self.location_type_land)
        # self.filter_layout_1_land.addWidget(self.purpose_type_land)
        self.filter_layout_1_land.addWidget(self.label_key_land)
        self.filter_layout_1_land.addWidget(self.keywords_land)
        self.filter_layout_1_land.addWidget(self.filter_button_land)
        page_land.addLayout(self.filter_layout_land)
        page_land.addLayout(self.filter_layout_1_land)

        # endblock filters
        # block preview
        self.data_view_layout_land = QtWidgets.QVBoxLayout()

        # block olx table
        self.olx_widget_land = QtWidgets.QWidget()
        self.layout_olx_land = QtWidgets.QVBoxLayout()
        self.label_rows_count_olx_land = QtWidgets.QLabel("Всего строк: 0")
        self.layout_olx_land.addWidget(self.label_rows_count_olx_land)
        self.olx_widget_land.setLayout(self.layout_olx_land)
        self.table_widget_olx_land = QtWidgets.QTableWidget()
        self.layout_olx_land.addWidget(self.table_widget_olx_land)
        self.data_view_layout_land.addWidget(self.olx_widget_land)
        page_land.addLayout(self.data_view_layout_land)
        page_land.addSpacing(10)
        page_land.setStretchFactor(self.data_view_layout_land, 1)
        return page_land

    def page_commerce_set(self, page_commerce, json_data=None):
        if json_data is not None and json_data["time_last_olx_commerce"]["h"] != -1:
            self.time_last_olx_commerce = QDateTime(
                json_data["time_last_olx_commerce"]["y"],
                json_data["time_last_olx_commerce"]["M"],
                json_data["time_last_olx_commerce"]["d"],
                json_data["time_last_olx_commerce"]["h"],
                json_data["time_last_olx_commerce"]["m"],
                0, 0)
            self.label_progress_bar_olx_commerce = QtWidgets.QLabel(
                f"Последнее обновление коммерции с OLX {self.time_last_olx_commerce.toString()}")
        else:
            self.time_last_olx_commerce = QDateTime()
            self.label_progress_bar_olx_commerce = QtWidgets.QLabel("Данные коммерции не загружены")

        self.update_layout_commerce = QtWidgets.QHBoxLayout()
        self.update_olx_commerce = QtWidgets.QPushButton("Обновить коммерцию")

        self.export_button_olx_commerce = QtWidgets.QPushButton("Экспорт в excel")

        self.update_layout_commerce.addWidget(self.update_olx_commerce)

        self.export_layout_commerce = QtWidgets.QHBoxLayout()
        self.export_layout_commerce.addWidget(self.export_button_olx_commerce)

        page_commerce.addLayout(self.export_layout_commerce)
        page_commerce.addLayout(self.update_layout_commerce)
        # block progress_bar

        self.progress_bar_layout_commerce = QtWidgets.QVBoxLayout()

        self.progress_bar_layout_commerce.addWidget(self.label_progress_bar_olx_commerce, 0)
        self.progress_bar_olx_commerce = QtWidgets.QProgressBar()
        self.progress_bar_layout_commerce.addWidget(self.progress_bar_olx_commerce, 0)
        self.progress_bar_olx_commerce.setProperty("value", 0)

        self.progress_bar_layout_commerce.addSpacing(10)
        self.progress_bar_layout_commerce.addStretch(1)
        page_commerce.addLayout(self.progress_bar_layout_commerce)
        # # block filters
        self.filter_layout_commerce = QtWidgets.QGridLayout()
        # # labels - first line
        self.label_category_commerce = QtWidgets.QLabel("Категория")
        self.label_price_commerce = QtWidgets.QLabel("Цена")
        self.label_square_commerce = QtWidgets.QLabel("Площадь")
        # self.label_type_of_commerce = QtWidgets.QLabel("Тип помещения")

        self.filter_button_commerce = QtWidgets.QPushButton("Отфильтровать")
        self.filter_layout_commerce.addWidget(self.label_category_commerce, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_commerce.addWidget(self.label_price_commerce, 0, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_commerce.addWidget(self.label_square_commerce, 0, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # inputs second line
        self.category_commerce = QtWidgets.QComboBox()
        self.price_min_commerce = QtWidgets.QLineEdit()
        self.price_min_commerce.setPlaceholderText("min")
        self.price_min_commerce.setValidator(QIntValidator(1, 999999999, self))
        self.price_max_commerce = QtWidgets.QLineEdit()
        self.price_max_commerce.setPlaceholderText("max")
        self.price_max_commerce.setValidator(QIntValidator(1, 999999999, self))
        self.currency_type_commerce = QtWidgets.QComboBox()
        self.square_min_commerce = QtWidgets.QLineEdit()
        self.square_max_commerce = QtWidgets.QLineEdit()
        self.square_max_commerce.setValidator(QIntValidator(1, 10000, self))
        self.square_min_commerce.setValidator(QIntValidator(1, 10000, self))
        self.square_max_commerce.setPlaceholderText("max")
        self.square_min_commerce.setPlaceholderText("min")
        self.type_commerce = QtWidgets.QComboBox()
        self.time_temp = QTime(0, 0, 0)
        self.filter_layout_commerce.addWidget(self.category_commerce, 2, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_commerce.addWidget(self.price_min_commerce, 2, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_commerce.addWidget(self.price_max_commerce, 2, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_commerce.addWidget(self.square_min_commerce, 2, 3, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_commerce.addWidget(self.square_max_commerce, 2, 4, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_commerce.addWidget(self.type_commerce, 2, 5, 1, 2, Qt.AlignmentFlag.AlignCenter)

        self.label_cur_commerce = QtWidgets.QLabel("Валюта")
        self.keywords_commerce = QtWidgets.QLineEdit()
        self.label_key_commerce = QtWidgets.QLabel("Ключевые слова")
        self.keywords_commerce.setPlaceholderText("слово1;слово2...")
        # self.time_fixed = QTime()
        self.filter_layout_1_commerce = QtWidgets.QHBoxLayout()
        # self.filter_layout_commerce.addWidget(self.repair_type_commerce, 2, 9, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_1_commerce.addWidget(self.label_cur_commerce)
        self.filter_layout_1_commerce.addWidget(self.currency_type_commerce)
        # self.filter_layout_1_commerce.addWidget(self.is_new_building_type_commerce)
        # self.filter_layout_1_commerce.addWidget(self.room_type_commerce)
        self.filter_layout_1_commerce.addWidget(self.label_key_commerce)
        self.filter_layout_1_commerce.addWidget(self.keywords_commerce)
        self.filter_layout_1_commerce.addWidget(self.filter_button_commerce)
        page_commerce.addLayout(self.filter_layout_commerce)
        page_commerce.addLayout(self.filter_layout_1_commerce)

        # endblock filters
        # block preview
        self.data_view_layout_commerce = QtWidgets.QVBoxLayout()

        # block olx table
        self.olx_widget_commerce = QtWidgets.QWidget()
        self.layout_olx_commerce = QtWidgets.QVBoxLayout()
        self.label_rows_count_olx_commerce = QtWidgets.QLabel("Всего строк: 0")
        self.layout_olx_commerce.addWidget(self.label_rows_count_olx_commerce)
        self.olx_widget_commerce.setLayout(self.layout_olx_commerce)
        self.table_widget_olx_commerce = QtWidgets.QTableWidget()
        self.layout_olx_commerce.addWidget(self.table_widget_olx_commerce)
        self.data_view_layout_commerce.addWidget(self.olx_widget_commerce)
        page_commerce.addLayout(self.data_view_layout_commerce)
        page_commerce.addSpacing(10)
        page_commerce.setStretchFactor(self.data_view_layout_commerce, 1)
        return page_commerce

    def show(self):
        super().show()

    def seria(self):
        if not os.path.exists("_internal/input/dumps"):
            os.mkdir("_internal/input/dumps")
        # print(self.time_fixed)
        time_fixed = {
            "h": self.time_fixed.hour(),
            "m": self.time_fixed.minute()
        }

        time_last_olx_flat = {
            "h": self.time_last_olx_flat.time().hour(),
            "m": self.time_last_olx_flat.time().minute(),
            "d": self.time_last_olx_flat.date().day(),
            "M": self.time_last_olx_flat.date().month(),
            "y": self.time_last_olx_flat.date().year(),

        }

        time_last_olx_land = {
            "h": self.time_last_olx_land.time().hour(),
            "m": self.time_last_olx_land.time().minute(),
            "d": self.time_last_olx_land.date().day(),
            "M": self.time_last_olx_land.date().month(),
            "y": self.time_last_olx_land.date().year(),

        }

        time_last_olx_commerce = {
            "h": self.time_last_olx_commerce.time().hour(),
            "m": self.time_last_olx_commerce.time().minute(),
            "d": self.time_last_olx_commerce.date().day(),
            "M": self.time_last_olx_commerce.date().month(),
            "y": self.time_last_olx_commerce.date().year(),

        }

        with open('_internal/input/dumps/dump.json', 'w') as file:
            json.dump({
                "time_fixed": time_fixed,
                "time_last_olx_land": time_last_olx_land,
                "time_last_olx_commerce": time_last_olx_commerce,
                "time_last_olx_flat": time_last_olx_flat
            }, file)
        print("dump done before closing")

    def closeEvent(self, event):
        can_be_closed = True
        for i in self.can_be_closed:
            can_be_closed = can_be_closed and i
        if not can_be_closed:
            message = QMessageBox()
            message.setWindowTitle("MAEParser")
            message.setWindowIcon(QIcon('_internal/input/icon.ico'))
            message.setText("Процесс скачивания продолжается! Вы уверены, что хотите закрыть приложение? ")
            message.setIcon(QMessageBox.Icon.Question)
            close = message.addButton("Закрыть", QMessageBox.ButtonRole.YesRole)
            message.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            message.exec()
            if close == message.clickedButton():
                self.seria()
                log_out.close()
                event.accept()

            else:
                event.ignore()
        else:
            self.seria()
            log_out.close()
            event.accept()

    def add_items_for_combo_box(self):
        self.type_commerce.addItems(COMMERCE_CHOICES)
        self.purpose_type_land.addItems(LAND_TYPE_CHOICES)
        self.location_type_land.addItems(LAND_LOCATION_CHOICES)
        self.is_new_building_type_flat.addItems(["Тип квартиры", "Новостройка", "Вторичный"])
        self.room_type_flat.addItems(["Кол-во комнат", "Студия", "1", "2", "3", "4", "5", "6+"])
        self.currency_type_flat.addItems(CURRENCY_CHOICES)
        self.category_flat.addItems(["Не выбрано", "Продажа", "Долгосрочная аренда", "Посуточная аренда"])
        self.category_commerce.addItems(["Не выбрано", "Продажа", "Аренда"])
        self.category_land.addItems(["Не выбрано", "Продажа", "Аренда"])
        self.currency_type_land.addItems(CURRENCY_CHOICES)
        self.currency_type_commerce.addItems(CURRENCY_CHOICES)
        self.repair_type_flat.addItems([REPAIR_CHOICES_UYBOR[one] for one in REPAIR_CHOICES_UYBOR])

    def block_close_olx_flat(self, block_closing):
        # self.block_post(block_closing, True, 0)
        self.can_be_closed[3] = not block_closing

    def block_close_olx_commerce(self, block_closing):
        # self.block_post(block_closing, True, 1)
        self.can_be_closed[4] = not block_closing

    def block_close_olx_land(self, block_closing):
        # self.block_post(block_closing, True, 2)
        self.can_be_closed[5] = not block_closing

    def block_close_olx_export_land(self, block_closing):
        # print(can_be_closed)
        self.can_be_closed[7] = not block_closing

    def block_close_olx_export_flat(self, block_closing):
        # print(can_be_closed)
        self.can_be_closed[9] = not block_closing

    def block_close_olx_export_commerce(self, block_closing):
        # print(can_be_closed)
        self.can_be_closed[11] = not block_closing

    def block(self, boolen, str_):
        if str_ != "uybor":
            self.export_button_olx_flat.setDisabled(boolen)

    def flat_olx_finished_thread(self):
        self.thread_olx_flat.deleteLater()
        print(f"last update olx flat {self.time_last_olx_flat.toString()}")
        self.update_olx_flat.setDisabled(False)

        self.filter_button_clicked(0)
        self.export_button_olx_flat.setEnabled(True)

    def commerce_olx_finished_thread(self):
        self.thread_olx_commerce.deleteLater()
        print(f"last update olx commerce {self.time_last_olx_commerce.toString()}")
        self.update_olx_commerce.setDisabled(False)

        self.filter_button_clicked(1)
        self.export_button_olx_commerce.setEnabled(True)

    def land_olx_finished_thread(self):
        self.thread_olx_land.deleteLater()
        print(f"last update olx land {self.time_last_olx_land.toString()}")
        self.update_olx_land.setDisabled(False)

        self.filter_button_clicked(2)
        self.export_button_olx_land.setEnabled(True)

    def show_message_with_exit(self, text):
        self.show_message_info(text)
        sys.exit()

    def show_message_info(self, text):
        self.message.setText(text)
        if "сохранен" in text:
            self.message.setIcon(QMessageBox.Icon.Information)
        else:
            self.message.setIcon(QMessageBox.Icon.Critical)
        self.message.show()

    def update_progress_bar(self, value, real_estate_type, domain):
        match real_estate_type + domain:
            case 'flatolx':
                self.progress_bar_olx_flat.setProperty("value", value)
            case 'commerceolx':
                self.progress_bar_olx_commerce.setProperty("value", value)
            case 'landolx':
                self.progress_bar_olx_land.setProperty("value", value)

    def update_label(self, value, real_estate_type, domain):
        match real_estate_type + domain:
            case 'flatolx':
                self.label_progress_bar_olx_flat.setText(
                    f"{value}. Последнее обновление: {self.time_last_olx_flat.toString()}")
            case 'commerceolx':
                self.label_progress_bar_olx_commerce.setText(
                    f"{value}. Последнее обновление: {self.time_last_olx_commerce.toString()}")
            case 'landolx':
                self.label_progress_bar_olx_land.setText(
                    f"{value}. Последнее обновление: {self.time_last_olx_land.toString()}")

    def update_date(self, results, real_estate_type, domain):
        match real_estate_type + domain:

            case 'flatolx':
                self.results_olx_flat = results
                self.filter_button_clicked(0)
                self.time_last_olx_flat = self.time_last_olx_flat.currentDateTime(QTimeZone.systemTimeZone())

            case 'commerceolx':
                self.results_olx_commerce = results
                self.filter_button_clicked(1)
                self.time_last_olx_commerce = self.time_last_olx_commerce.currentDateTime(QTimeZone.systemTimeZone())

            case 'landolx':
                self.results_olx_land = results
                self.filter_button_clicked(2)
                self.time_last_olx_land = self.time_last_olx_land.currentDateTime(QTimeZone.systemTimeZone())

    def update_results(self, results, real_estate_type, domain):
        if domain == 'olx':
            match real_estate_type:
                case 'flat':
                    self.results_olx_flat = results
                    # self.data_view.setCurrentIndex(0)
                    self.filter_button_clicked(0)
                    # self.time_last_uybor_flat = self.time_last_uybor_flat.currentDateTime(QTimeZone.systemTimeZone())
                case 'commerce':
                    self.results_olx_commerce = results
                    # self.data_view.setCurrentIndex(1)
                    self.filter_button_clicked(1)
                    # self.time_last_uybor_commerce = self.time_last_uybor_flat.currentDateTime(QTimeZone.systemTimeZone())
                case 'land':
                    self.results_olx_land = results
                    # self.data_view.setCurrentIndex(2)
                    self.filter_button_clicked(2)
                # self.time_last_uybor_land = self.time_last_uybor_flat.currentDateTime(QTimeZone.systemTimeZone())

    def time_clicked(self):
        self.set_time_button.setEnabled(False)
        now = datetime.datetime.now(tz)
        self.time_fixed = self.time_temp
        self.set_time_label_time.setText(f"Каждый день в {self.time_fixed.toString()}")
        if (now.hour > self.time_temp.hour() or
                (now.hour == self.time_temp.hour() and now.minute > self.time_temp.minute())):
            msec = 1000 * 60 * (24 * 60 - (now.hour * 60 + now.minute)
                                + self.time_temp.hour() * 60 + self.time_temp.minute())

        else:
            msec = 1000 * 60 * ((now.hour * 60 + now.minute) -
                                self.time_temp.hour() * 60 - self.time_temp.minute()) * (-1)

        # self.timer.start(msec)

    def time_update(self):
        print(f"datatime updating start {datetime.datetime.now(tz).time()}")
        self.data_view.setCurrentIndex(0)
        self.update_olx_clicked()
        self.data_view.setCurrentIndex(1)
        self.update_olx_clicked()
        self.data_view.setCurrentIndex(2)
        self.update_olx_clicked()
        self.timer.setInterval(24 * 60 * 60 * 1000)

    def update_olx_clicked(self):
        match self.data_view.currentIndex():
            case 0:
                real_estate = 'flat'
                self.export_button_olx_flat.setDisabled(True)
                self.update_olx_flat.setDisabled(True)
                self.filter_button_flat.setEnabled(True)
                self.thread_olx_flat = DataFromDB("olx", self.rate, real_estate)
                self.thread_olx_flat.updated.connect(self.update_progress_bar)
                self.thread_olx_flat.throw_exception.connect(self.show_message_with_exit)
                self.thread_olx_flat.block_closing.connect(self.block_close_olx_flat)
                self.thread_olx_flat.throw_info.connect(self.show_message_info)
                self.thread_olx_flat.finished.connect(self.flat_olx_finished_thread)
                self.thread_olx_flat.label.connect(self.update_label)
                self.thread_olx_flat.date.connect(self.update_date)
                self.thread_olx_flat.init_flats.connect(self.update_results)
                self.thread_olx_flat.start()
            case 1:
                real_estate = 'commerce'
                self.export_button_olx_commerce.setDisabled(True)
                self.update_olx_commerce.setDisabled(True)
                self.filter_button_commerce.setEnabled(True)
                self.thread_olx_commerce = DataFromDB("olx", self.rate, real_estate)
                self.thread_olx_commerce.updated.connect(self.update_progress_bar)
                self.thread_olx_commerce.throw_exception.connect(self.show_message_with_exit)
                self.thread_olx_commerce.block_closing.connect(self.block_close_olx_commerce)
                self.thread_olx_commerce.throw_info.connect(self.show_message_info)
                self.thread_olx_commerce.finished.connect(self.commerce_olx_finished_thread)
                self.thread_olx_commerce.label.connect(self.update_label)
                self.thread_olx_commerce.date.connect(self.update_date)
                self.thread_olx_commerce.init_flats.connect(self.update_results)
                self.thread_olx_commerce.start()
            case 2:
                real_estate = 'land'
                self.export_button_olx_land.setDisabled(True)
                self.update_olx_land.setDisabled(True)
                self.filter_button_land.setEnabled(True)
                self.thread_olx_land = DataFromDB("olx", self.rate, real_estate)
                self.thread_olx_land.updated.connect(self.update_progress_bar)
                self.thread_olx_land.throw_exception.connect(self.show_message_with_exit)
                self.thread_olx_land.block_closing.connect(self.block_close_olx_land)
                self.thread_olx_land.throw_info.connect(self.show_message_info)
                self.thread_olx_land.finished.connect(self.land_olx_finished_thread)
                self.thread_olx_land.label.connect(self.update_label)
                self.thread_olx_land.date.connect(self.update_date)
                self.thread_olx_land.init_flats.connect(self.update_results)
                self.thread_olx_land.start()

    def filter_button_clicked(self, page_filter=None):
        # print("1")
        if 'uzs' in self.filters:
            cur = 'uzs'
        else:
            cur = 'uye'
        print(self.filters)
        if not page_filter:
            page_filter = self.data_view.currentIndex()
        match page_filter:
            case 0:

                self.results_olx_flat_filtered = filtration(filters=self.filters[0], results=self.results_olx_flat,
                                                            type_of_re='flat')
                self.label_rows_count_olx_flat.setText(f"Выборка: {len(self.results_olx_flat_filtered)}/"
                                                       f"{len(self.results_olx_flat)}")
                fill_table_pyqt(self.table_widget_olx_flat, header_flat, self.results_olx_flat_filtered,
                                cur, self.s_, self.f_, )
                self.export_button_olx_flat.setEnabled(len(self.results_olx_flat_filtered) > 0
                                                       and self.update_olx_flat.isEnabled())
                # self.show_message_info(f"{len(self.results_uybor_f)} + {len(self.results_olx_f)}")
            case 1:

                self.results_olx_commerce_filtered = filtration(filters=self.filters[1],
                                                                results=self.results_olx_commerce,
                                                                type_of_re='commerce')
                self.label_rows_count_olx_commerce.setText(f"Выборка: {len(self.results_olx_commerce_filtered)}/"
                                                           f"{len(self.results_olx_commerce)}")
                fill_table_pyqt(self.table_widget_olx_commerce, header_commerce, self.results_olx_commerce_filtered,
                                cur,
                                self.s_, self.f_, 5)
                self.export_button_olx_commerce.setEnabled(len(self.results_olx_commerce_filtered) > 0
                                                           and self.update_olx_commerce.isEnabled())
                # self.show_message_info(f"{len(self.results_uybor_f)} + {len(self.results_olx_f)}")

            case 2:

                self.results_olx_land_filtered = filtration(filters=self.filters[2], results=self.results_olx_land,
                                                            type_of_re='land')
                self.label_rows_count_olx_land.setText(f"Выборка: {len(self.results_olx_land_filtered)}/"
                                                       f"{len(self.results_olx_land)}")
                fill_table_pyqt(self.table_widget_olx_land, header_land, self.results_olx_land_filtered, cur, self.s_,
                                self.f_, 5)
                self.export_button_olx_land.setEnabled(len(self.results_olx_land_filtered) > 0
                                                       and self.update_olx_land.isEnabled())

    def export_button_clicked_olx(self):

        match self.data_view.currentIndex():
            case 0:
                real_estate = 'flat'
                self.export_button_olx_flat.setDisabled(True)
                results = self.results_olx_flat_filtered
                self.thread_export_olx_flat = Exporter(name="olx", results=results, type_real_estate=real_estate)
                self.thread_export_olx_flat.throw_exception.connect(self.show_message_with_exit)
                self.thread_export_olx_flat.throw_info.connect(self.show_message_info)
                self.thread_export_olx_flat.finished.connect(self.finised_export_olx_flat)
                self.thread_export_olx_flat.block_closing.connect(self.block_close_olx_export_flat)
                self.thread_export_olx_flat.start()
            case 1:
                real_estate = 'commerce'
                self.export_button_olx_commerce.setDisabled(True)
                results = self.results_olx_commerce_filtered
                self.thread_export_olx_commerce = Exporter(name="olx", results=results, type_real_estate=real_estate)
                self.thread_export_olx_commerce.throw_exception.connect(self.show_message_with_exit)
                self.thread_export_olx_commerce.throw_info.connect(self.show_message_info)
                self.thread_export_olx_commerce.finished.connect(self.finised_export_olx_commerce)
                self.thread_export_olx_commerce.block_closing.connect(self.block_close_olx_export_commerce)
                self.thread_export_olx_commerce.start()
            case 2:
                real_estate = 'land'
                self.export_button_olx_land.setDisabled(True)
                results = self.results_olx_land_filtered
                self.thread_export_olx_land = Exporter(name="olx", results=results, type_real_estate=real_estate)
                self.thread_export_olx_land.throw_exception.connect(self.show_message_with_exit)
                self.thread_export_olx_land.throw_info.connect(self.show_message_info)
                self.thread_export_olx_land.finished.connect(self.finised_export_olx_land)
                self.thread_export_olx_land.block_closing.connect(self.block_close_olx_export_land)
                self.thread_export_olx_land.start()
            case _:
                return

    def finised_export_olx_land(self):
        self.thread_export_olx_land.deleteLater()
        self.export_button_olx_land.setDisabled(False)

    def finised_export_olx_flat(self):
        self.thread_export_olx_flat.deleteLater()
        self.export_button_olx_flat.setDisabled(False)

    def finised_export_olx_commerce(self):
        self.thread_export_olx_commerce.deleteLater()
        self.export_button_olx_commerce.setDisabled(not True)

    def export_button_clicked(self):
        self.export_button_clicked_olx()

    def cur_chosen(self):
        self.filter_button_flat.setEnabled(True)
        match self.data_view.currentIndex():
            case 0:
                if self.currency_type_flat.currentText() == "СУММ.":
                    self.filters[0].update({"uzs": True})
                    self.table_widget_olx_flat.setColumnHidden(11, False)
                    self.table_widget_olx_flat.setColumnHidden(10, False)
                    self.table_widget_olx_flat.setColumnHidden(8, True)
                    self.table_widget_olx_flat.setColumnHidden(9, True)

                    if "uye" in self.filters[0]:
                        self.filters[0].pop("uye")
                else:
                    self.filters[0].update({"uye": True})

                    self.table_widget_olx_flat.setColumnHidden(8, False)
                    self.table_widget_olx_flat.setColumnHidden(9, False)
                    self.table_widget_olx_flat.setColumnHidden(10, True)
                    self.table_widget_olx_flat.setColumnHidden(11, True)
                    if "uzs" in self.filters[0]:
                        self.filters[0].pop("uzs")
            case 1:
                if self.currency_type_commerce.currentText() == "СУММ.":
                    self.filters[1].update({"uzs": True})
                    self.table_widget_olx_commerce.setColumnHidden(8, False)
                    self.table_widget_olx_commerce.setColumnHidden(7, False)
                    self.table_widget_olx_commerce.setColumnHidden(5, True)
                    self.table_widget_olx_commerce.setColumnHidden(6, True)
                    if "uye" in self.filters[1]:
                        self.filters[1].pop("uye")
                else:
                    self.filters[1].update({"uye": True})
                    self.table_widget_olx_commerce.setColumnHidden(5, False)
                    self.table_widget_olx_commerce.setColumnHidden(6, False)
                    self.table_widget_olx_commerce.setColumnHidden(7, True)
                    self.table_widget_olx_commerce.setColumnHidden(8, True)
                    if "uzs" in self.filters[1]:
                        self.filters[1].pop("uzs")

            case 2:
                if self.currency_type_land.currentText() == "СУММ.":
                    self.filters[2].update({"uzs": True})
                    self.table_widget_olx_land.setColumnHidden(8, False)
                    self.table_widget_olx_land.setColumnHidden(7, False)
                    self.table_widget_olx_land.setColumnHidden(5, True)
                    self.table_widget_olx_land.setColumnHidden(6, True)
                    if "uye" in self.filters[2]:
                        self.filters[2].pop("uye")
                else:
                    self.filters[2].update({"uye": True})
                    self.table_widget_olx_land.setColumnHidden(5, False)
                    self.table_widget_olx_land.setColumnHidden(6, False)
                    self.table_widget_olx_land.setColumnHidden(7, True)
                    self.table_widget_olx_land.setColumnHidden(8, True)
                    if "uzs" in self.filters[2]:
                        self.filters[2].pop("uzs")

    def room_chosen(self):
        self.filter_button_flat.setEnabled(True)
        if self.room_type_flat.currentText() != "Кол-во комнат":
            self.filters[0].update({"room": self.room_type_flat.currentText()})
        else:
            if "room" in self.filters[0]:
                self.filters[0].pop("room")

    def is_new_building_chosen(self):
        self.filter_button_flat.setEnabled(True)
        if self.is_new_building_type_flat.currentText() != "Тип квартиры":
            self.filters[0].update({"is_new_building": self.is_new_building_type_flat.currentText()})
        else:
            if "is_new_building" in self.filters[0]:
                self.filters[0].pop("is_new_building")
        # time.sleep(1)

    def repair_chosen(self):
        self.filter_button_flat.setEnabled(True)

        if self.repair_type_flat.currentText() != "Ремонт":
            self.filters[0].update({"repair": REPAIR_CHOICES_UYBOR.index(self.repair_type_flat.currentText())})
        else:
            if "repair" in self.filters[0]:
                self.filters[0].pop("repair")

    def commerce_type_chosen(self):
        self.filter_button_flat.setEnabled(True)
        if self.type_commerce.currentText() != "Тип помещения":
            self.filters[1].update({"type": self.type_commerce.currentText()})
        else:
            if "type" in self.filters[1]:
                self.filters[1].pop("type")

    def land_purpose_chosen(self):
        self.filter_button_flat.setEnabled(True)

        if self.purpose_type_land.currentIndex() != 0:
            self.filters[2].update({"purpose": self.purpose_type_land.currentText()})
        else:
            if "purpose" in self.filters[2]:
                self.filters[2].pop("purpose")

    def land_location_chosen(self):
        self.filter_button_flat.setEnabled(True)

        if self.location_type_land.currentIndex() != 0:
            self.filters[2].update({"location": self.location_type_land.currentText()})
        else:
            if "location" in self.filters[2]:
                self.filters[2].pop("location")

    def price_min_changed(self):
        self.filter_button_flat.setEnabled(True)
        match self.data_view.currentIndex():
            case 0:
                if self.price_min_flat.text() != "":
                    self.filters[0].update({"price_min": int(self.price_min_flat.text())})
                else:
                    if "price_min" in self.filters[0]:
                        self.filters[0].pop("price_min")
            case 1:
                if self.price_min_commerce.text() != "":
                    self.filters[1].update({"price_min": int(self.price_min_commerce.text())})
                else:
                    if "price_min" in self.filters[1]:
                        self.filters[1].pop("price_min")
            case 2:
                if self.price_min_land.text() != "":
                    self.filters[2].update({"price_min": int(self.price_min_land.text())})
                else:
                    if "price_min" in self.filters[2]:
                        self.filters[2].pop("price_min")

    def price_max_changed(self):
        self.filter_button_flat.setEnabled(True)
        match self.data_view.currentIndex():
            case 0:
                if self.price_max_flat.text() != "":
                    self.filters[0].update({"price_max": int(self.price_max_flat.text())})
                else:
                    if "price_max" in self.filters[0]:
                        self.filters[0].pop("price_max")
            case 1:
                if self.price_max_commerce.text() != "":
                    self.filters[1].update({"price_max": int(self.price_max_commerce.text())})
                else:
                    if "price_max" in self.filters[1]:
                        self.filters[1].pop("price_max")
            case 2:
                if self.price_max_land.text() != "":
                    self.filters[2].update({"price_max": int(self.price_max_land.text())})
                else:
                    if "price_max" in self.filters[2]:
                        self.filters[2].pop("price_max")

    def time_changed(self):
        self.set_time_button.setEnabled(True)
        if self.set_time_input.text() != "":
            self.time_temp = self.set_time_input.time()

    def keyword_changed(self):
        self.filter_button_flat.setEnabled(True)

        match self.data_view.currentIndex():
            case 0:
                if self.keywords_flat.text() != "":
                    self.filters[0].update({"keywords": self.keywords_flat.text()})
                else:
                    if "keywords" in self.filters[0]:
                        self.filters[0].pop("keywords")
            case 1:
                if self.keywords_commerce.text() != "":
                    self.filters[1].update({"keywords": self.keywords_commerce.text()})
                else:
                    if "keywords" in self.filters[1]:
                        self.filters[1].pop("keywords")

            case 2:
                if self.keywords_land.text() != "":
                    self.filters[2].update({"keywords": self.keywords_land.text()})
                else:
                    if "keywords" in self.filters[2]:
                        self.filters[2].pop("keywords")

    def floor_min_changed(self):
        self.filter_button_flat.setCheckable(True)
        if self.floor_min_flat.text() != "":
            self.filters[0].update({"floor_min": int(self.floor_min_flat.text())})
        else:
            if "floor_min" in self.filters[0]:
                self.filters[0].pop("floor_min")

    def floor_max_changed(self):
        self.filter_button_flat.setEnabled(True)
        if self.floor_max_flat.text() != "":
            self.filters[0].update({"floor_max": int(self.floor_max_flat.text())})
        else:
            if "floor_max" in self.filters[0]:
                self.filters[0].pop("floor_max")

    def square_min_changed(self):
        self.filter_button_flat.setEnabled(True)
        match self.data_view.currentIndex():
            case 0:
                if self.square_min_flat.text() != "":
                    self.filters[0].update({"square_min": int(self.square_min_flat.text())})
                else:
                    if "square_min" in self.filters[0]:
                        self.filters[0].pop("square_min")
            case 1:
                if self.square_min_commerce.text() != "":
                    self.filters[1].update({"square_min": int(self.square_min_commerce.text())})
                else:
                    if "square_min" in self.filters[1]:
                        self.filters[1].pop("square_min")
            case 2:
                if self.square_min_land.text() != "":
                    self.filters[2].update({"square_min": int(self.square_min_land.text())})
                else:
                    if "square_min" in self.filters[2]:
                        self.filters[2].pop("square_min")

    def category_changed(self):
        self.filter_button_flat.setEnabled(True)

        match self.data_view.currentIndex():
            case 0:
                if self.category_flat.currentText() != "Не выбрано":
                    self.filters[0].update({"category": self.category_flat.currentText()})
                else:
                    if "category" in self.filters[0]:
                        self.filters[0].pop("category")

            case 1:
                if self.category_commerce.currentText() != "Не выбрано":
                    self.filters[1].update({"category": self.category_commerce.currentText()})
                else:
                    if "category" in self.filters[1]:
                        self.filters[1].pop("category")
            case 2:
                if self.category_land.currentText() != "Не выбрано":
                    self.filters[2].update({"category": self.category_land.currentText()})
                else:
                    if "category" in self.filters[2]:
                        self.filters[2].pop("category")

    def square_max_changed(self):
        self.filter_button_flat.setEnabled(True)

        if self.square_max_flat.text() != "":
            self.filters[self.data_view.currentIndex()].update({"square_max": int(self.square_max_flat.text())})
        else:
            if "square_max" in self.filters[self.data_view.currentIndex()]:
                self.filters[self.data_view.currentIndex()].pop("square_max")

    def total_floor_min_changed(self):
        self.filter_button_flat.setEnabled(True)

        if self.total_floor_min_flat.text() != "":
            self.filters[0].update({"total_floor_min": int(self.total_floor_min_flat.text())})
        else:
            if "total_floor_min" in self.filters[0]:
                self.filters[0].pop("total_floor_min")

    def total_floor_max_changed(self):
        self.filter_button_flat.setEnabled(True)

        if self.total_floor_max_flat.text() != "":
            self.filters[0].update({"total_floor_max": int(self.total_floor_max_flat.text())})
        else:
            if "total_floor_max" in self.filters[0]:
                self.filters[0].pop("total_floor_max")

    def start_upload(self):
        self.upload_olx_flat = UploadOlx(self.results_olx_flat, 'flat')
        self.upload_olx_flat.finished.connect(self.upload_olx_finished_flat)
        # self.upload_olx_flat.init_update_db.connect(self.answer_to_init_update)
        self.upload_olx_flat.start()
        self.upload_olx_land = UploadOlx(self.results_olx_land, 'land')
        self.upload_olx_land.finished.connect(self.upload_olx_finished_land)
        # self.upload_olx_land.init_update_db.connect(self.answer_to_init_update)
        self.upload_olx_land.start()
        self.upload_olx_commerce = UploadOlx(self.results_olx_commerce, 'commerce')
        self.upload_olx_commerce.finished.connect(self.upload_olx_finished_commerce)
        # self.upload_olx_commerce.init_update_db.connect(self.answer_to_init_update)
        self.upload_olx_commerce.start()

    def handler(self):
        self.start_upload()
        self.set_time_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.set_time_button.clicked.connect(self.time_clicked)
        self.room_type_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.repair_type_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.currency_type_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.is_new_building_type_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.progress_bar_olx_flat.setCursor(QCursor(Qt.CursorShape.BusyCursor))

        self.room_type_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.repair_type_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.currency_type_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.is_new_building_type_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.progress_bar_olx_flat.setCursor(QCursor(Qt.CursorShape.BusyCursor))

        self.room_type_flat.activated.connect(self.room_chosen)
        self.repair_type_flat.activated.connect(self.repair_chosen)
        self.currency_type_flat.activated.connect(self.cur_chosen)
        self.currency_type_land.activated.connect(self.cur_chosen)
        self.currency_type_commerce.activated.connect(self.cur_chosen)
        self.category_flat.activated.connect(self.category_changed)
        self.category_commerce.activated.connect(self.category_changed)
        self.category_land.activated.connect(self.category_changed)
        self.location_type_land.activated.connect(self.land_location_chosen)
        self.purpose_type_land.activated.connect(self.land_purpose_chosen)
        self.type_commerce.activated.connect(self.commerce_type_chosen)

        self.is_new_building_type_flat.activated.connect(self.is_new_building_chosen)

        self.export_button_olx_commerce.clicked.connect(self.export_button_clicked_olx)
        self.export_button_olx_flat.clicked.connect(self.export_button_clicked_olx)
        self.export_button_olx_land.clicked.connect(self.export_button_clicked_olx)
        self.update_olx_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.update_olx_commerce.clicked.connect(self.update_olx_clicked)
        self.update_olx_land.clicked.connect(self.update_olx_clicked)
        self.update_olx_flat.clicked.connect(self.update_olx_clicked)
        self.filter_button_land.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.filter_button_land.clicked.connect(self.filter_button_clicked)
        self.filter_button_commerce.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.filter_button_commerce.clicked.connect(self.filter_button_clicked)
        self.filter_button_flat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.filter_button_flat.clicked.connect(self.filter_button_clicked)
        self.price_min_flat.textChanged.connect(self.price_min_changed)
        self.price_max_flat.textChanged.connect(self.price_max_changed)
        self.price_max_land.textChanged.connect(self.price_min_changed)
        self.price_max_land.textChanged.connect(self.price_max_changed)
        self.price_min_commerce.textChanged.connect(self.price_min_changed)
        self.price_max_commerce.textChanged.connect(self.price_max_changed)
        self.square_min_flat.textChanged.connect(self.square_min_changed)
        self.square_max_commerce.textChanged.connect(self.square_max_changed)
        self.square_min_commerce.textChanged.connect(self.square_min_changed)
        self.square_max_land.textChanged.connect(self.square_max_changed)
        self.square_min_land.textChanged.connect(self.square_min_changed)
        self.square_max_flat.textChanged.connect(self.square_max_changed)
        self.floor_min_flat.textChanged.connect(self.floor_min_changed)
        self.floor_max_flat.textChanged.connect(self.floor_max_changed)
        self.keywords_flat.textChanged.connect(self.keyword_changed)
        self.keywords_commerce.textChanged.connect(self.keyword_changed)
        self.keywords_land.textChanged.connect(self.keyword_changed)
        self.total_floor_max_flat.textChanged.connect(self.total_floor_max_changed)
        self.total_floor_min_flat.textChanged.connect(self.total_floor_min_changed)
        self.set_time_input.timeChanged.connect(self.time_changed)

    def upload_olx_finished_flat(self):
        self.upload_olx_flat.deleteLater()

    def upload_olx_finished_commerce(self):
        self.upload_olx_commerce.deleteLater()

    def upload_olx_finished_land(self):
        self.upload_olx_land.deleteLater()


if not os.path.exists("_internal/output"):
    os.mkdir("_internal/output")
log_out = open(f'_internal/output/{datetime.datetime.now().strftime("%d-%m-%Y")}.txt', 'a', encoding="utf-8")
# log_err = open('_internal/output/log_err.txt', 'a', encoding="utf-8")

if __name__ == "__main__":
    # sys.stdout = log_out
    # sys.stderr = log_out
    app = QtWidgets.QApplication(sys.argv)
    print("version 27.06.2024")
    if not os.path.exists("output"):
        os.mkdir("output")
    if os.path.exists("_internal/input/dumps/dump.json"):
        with open("_internal/input/dumps/dump.json", 'r') as f:
            json_data = json.load(f)
            ui = UiParser(json_data)
            print(f"dump opened {datetime.datetime.now(tz)}")
    else:
        ui = UiParser()
    ui.show()
    app.setWindowIcon(QIcon('_internal/input/icon.ico'))
    ui.setWindowIcon(QIcon('_internal/input/icon.ico'))
    try:
        sys.exit(app.exec())
    except Exception as err:
        print("catch", err)
    finally:
        log_out.close()
