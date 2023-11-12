import asyncio
import datetime
import json
import os
import re
import sys
import time
from urllib.request import urlopen

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QTime, QTimer, QDateTime, QTimeZone
from PyQt6.QtGui import QIntValidator, QCursor, QIcon
from PyQt6.QtWidgets import QMessageBox
from bs4 import BeautifulSoup

from checker import Checker
from export import Exporter, fill_table_pyqt
from flat import CURRENCY_CHOISES, REPAIR_CHOICES_UYBOR, header
from getter_from_db import DataFromDB
from filtration import filtration
import pytz

from upload_olx import UploadOlx
from upload_uybor import UploadUybor

tz = pytz.timezone('Asia/Tashkent')


class UiParser(QtWidgets.QMainWindow):
    results_olx = []
    results_uybor = []
    results_olx_f = []
    results_uybor_f = []
    filters = {}

    def get_rate(self):
        # print("\tget rate")
        url = 'https://ofb.uz/uz/'
        # Request(url).add_header('Accept-Encoding', 'identity')
        while True:
            try:
                page = urlopen(url)
                html = page.read().decode('utf-8')
                soup = BeautifulSoup(html, "html.parser")
                curs = soup.find_all(name="div", attrs={"class": "currency"})
                return float(re.search(r"(\d+)\.(\d+)", curs[0].get_text())[0])
            except Exception as arr:
                print(arr, url, "rate")
                time.sleep(10)
                continue

    def __init__(self, json_data=None):
        super().__init__()
        self.rate = self.get_rate()
        self.s_ = 0
        self.f_ = 100
        self.uploaded_uybor = False
        print(f"time start app {datetime.datetime.now(tz=tz)}")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.time_update)
        self.set_time_label = QtWidgets.QLabel("Время обновления: ")
        self.set_time_button = QtWidgets.QPushButton("Настроить время обновления")
        self.set_time_label_time = QtWidgets.QLabel("Не выбрано")
        self.can_be_closed = [True, True, True, True]
        if json_data is not None and json_data["time_last_olx"]["h"] != -1:
            self.time_last_olx = QDateTime(
                json_data["time_last_olx"]["y"],
                json_data["time_last_olx"]["M"],
                json_data["time_last_olx"]["d"],
                json_data["time_last_olx"]["h"],
                json_data["time_last_olx"]["m"],
                0, 0)
            self.label_progress_bar_olx = QtWidgets.QLabel(
                f"Последнее обновление OLX {self.time_last_olx.toString()}")
        else:
            self.time_last_olx = QDateTime()
            self.label_progress_bar_olx = QtWidgets.QLabel("Данные с olx не загружены")
        if json_data is not None and json_data["time_last_uybor"]["h"] != -1:
            self.time_last_uybor = QDateTime(
                json_data["time_last_uybor"]["y"],
                json_data["time_last_uybor"]["M"],
                json_data["time_last_uybor"]["d"],
                json_data["time_last_uybor"]["h"],
                json_data["time_last_uybor"]["m"],
                0, 0)
            self.label_progress_bar_uybor = QtWidgets.QLabel(
                f"Последнее обновление UyBor {self.time_last_uybor.toString()}")
        else:
            self.time_last_uybor = QDateTime()
            self.label_progress_bar_uybor = QtWidgets.QLabel("Данные с uybor не загружены")
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
        self.setWindowTitle("MAEParser")
        self.main_widget = QtWidgets.QWidget()
        page_layout = QtWidgets.QVBoxLayout()
        self.message = QMessageBox(self)
        self.message.setWindowTitle("MAEParser")
        self.message.setWindowIcon(QIcon('_internal/input/icon.ico'))
        # block buttons upload
        self.set_time_layout = QtWidgets.QHBoxLayout()
        # self.set_time_button.setEnabled(False)

        self.set_time_layout.addWidget(self.set_time_label)
        self.set_time_layout.addWidget(self.set_time_label_time)
        self.set_time_layout.addWidget(self.set_time_input)
        self.set_time_layout.addWidget(self.set_time_button)
        page_layout.addLayout(self.set_time_layout)
        self.update_layout = QtWidgets.QHBoxLayout()
        self.update_olx = QtWidgets.QPushButton("Обновить OLx")
        self.update_uybor = QtWidgets.QPushButton("Обновить UyBor")
        self.update_all_data = QtWidgets.QPushButton("Обновить OLx и UyBor")

        self.export_button_olx = QtWidgets.QPushButton("Экспорт excel из OLx")
        self.export_button_uybor = QtWidgets.QPushButton("Экспорт excel из UyBor")
        self.export_button_all_data = QtWidgets.QPushButton("Экспорт excel из OLx и UyBor")

        self.update_layout.addWidget(self.update_uybor)
        self.update_layout.addWidget(self.update_olx)
        self.update_layout.addWidget(self.update_all_data)

        self.export_layout = QtWidgets.QHBoxLayout()
        self.export_layout.addWidget(self.export_button_uybor)
        self.export_layout.addWidget(self.export_button_olx)
        self.export_layout.addWidget(self.export_button_all_data)

        page_layout.addLayout(self.export_layout)
        page_layout.addLayout(self.update_layout)
        # block progress_bar

        self.progress_bar_layout = QtWidgets.QVBoxLayout()

        self.progress_bar_layout.addWidget(self.label_progress_bar_olx, 0)
        self.progress_bar_olx = QtWidgets.QProgressBar()
        self.progress_bar_layout.addWidget(self.progress_bar_olx, 0)
        self.progress_bar_olx.setProperty("value", 0)

        self.progress_bar_layout.addWidget(self.label_progress_bar_uybor, 0)
        self.progress_bar_uybor = QtWidgets.QProgressBar()
        self.progress_bar_layout.addWidget(self.progress_bar_uybor, 0)
        self.progress_bar_uybor.setProperty("value", 0)

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
        # self.filter_layout.addWidget(self.filter_button, 3, 9, 1, 2, Qt.AlignmentFlag.AlignCenter)
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
        self.time_temp = QTime(0, 0, 0)
        self.filter_layout.addWidget(self.price_min, 2, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.price_max, 2, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.square_min, 2, 3, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.square_max, 2, 4, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.floor_min, 2, 5, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.floor_max, 2, 6, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.total_floor_min, 2, 7, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.total_floor_max, 2, 8, 1, 1, Qt.AlignmentFlag.AlignCenter)
        # self.uploaded_uybor = False

        # self.threads = []
        # combo_boxs on second line
        self.room_type = QtWidgets.QComboBox()
        self.repair_type = QtWidgets.QComboBox()
        self.is_new_building_type = QtWidgets.QComboBox()
        self.label_cur = QtWidgets.QLabel("Валюта")
        self.keywords = QtWidgets.QLineEdit()
        self.label_key = QtWidgets.QLabel("Ключевые слова")
        self.keywords.setPlaceholderText("слово1;слово2...")
        # self.time_fixed = QTime()
        self.filter_layout_1 = QtWidgets.QHBoxLayout()
        self.filter_layout.addWidget(self.repair_type, 2, 9, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.filter_layout_1.addWidget(self.label_cur)
        self.filter_layout_1.addWidget(self.currency_type)
        self.filter_layout_1.addWidget(self.is_new_building_type)
        self.filter_layout_1.addWidget(self.room_type)
        self.filter_layout_1.addWidget(self.label_key)
        self.filter_layout_1.addWidget(self.keywords)
        self.filter_layout_1.addWidget(self.filter_button)
        page_layout.addLayout(self.filter_layout)
        page_layout.addLayout(self.filter_layout_1)
        self.filters.update({"uzs": True})
        # endblock filters
        # block preview
        self.data_view_layout = QtWidgets.QVBoxLayout()
        # self.label_preview = QtWidgets.QLabel("Предпросмотр")
        self.data_view = QtWidgets.QTabWidget()
        # self.data_view.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # self.data_view_layout.addWidget(self.label_preview)
        self.data_view_layout.addWidget(self.data_view)

        # block uybor table
        self.uybor_widget = QtWidgets.QWidget()
        self.layout_uybor = QtWidgets.QVBoxLayout()
        self.label_rows_count_uybor = QtWidgets.QLabel("Всего строк: 0")
        self.layout_uybor.addWidget(self.label_rows_count_uybor)
        self.uybor_widget.setLayout(self.layout_uybor)
        self.table_widget_uybor = QtWidgets.QTableWidget()
        self.table_widget_uybor.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.layout_uybor.addWidget(self.table_widget_uybor)
        self.layout_uybor.setStretchFactor(self.table_widget_uybor, 1)
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
        self.data_view_layout.setStretchFactor(self.layout_uybor, 1)
        page_layout.addLayout(self.data_view_layout)
        page_layout.addSpacing(10)
        page_layout.setStretchFactor(self.data_view_layout, 1)
        self.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(page_layout)
        self.setCentralWidget(self.main_widget)
        self.add_items_for_combo_box()
        self.handler()
        self.filter_button_clicked()
        # self.setup_upload()

    def seria(self):
        if not os.path.exists("_internal/input/dumps"):
            os.mkdir("_internal/input/dumps")
        # print(self.time_fixed)
        time_fixed = {
            "h": self.time_fixed.hour(),
            "m": self.time_fixed.minute()
        }
        time_last_uybor = {
            "h": self.time_last_uybor.time().hour(),
            "m": self.time_last_uybor.time().minute(),
            "d": self.time_last_uybor.date().day(),
            "M": self.time_last_uybor.date().month(),
            "y": self.time_last_uybor.date().year(),
        }
        time_last_olx = {
            "h": self.time_last_olx.time().hour(),
            "m": self.time_last_olx.time().minute(),
            "d": self.time_last_olx.date().day(),
            "M": self.time_last_olx.date().month(),
            "y": self.time_last_olx.date().year(),

        }

        with open('_internal/input/dumps/dump.json', 'w') as file:
            json.dump({
                "time_fixed": time_fixed,
                "time_last_uybor": time_last_uybor,
                "time_last_olx": time_last_olx
            }, file)
        print("dump done before closing")

    def closeEvent(self, event):
        if (not self.can_be_closed[0] or not self.can_be_closed[1]
                or not self.can_be_closed[2] or not self.can_be_closed[3]):
            message = QMessageBox()
            message.setWindowTitle("MAEParser")
            message.setWindowIcon(QIcon('_internal/input/icon.ico'))
            message.setText("Процесс скачивания продожается! Вы уверены, что хотите закрыть приложение? ")
            message.setIcon(QMessageBox.Icon.Question)
            close = message.addButton("Закрыть", QMessageBox.ButtonRole.YesRole)
            message.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            message.exec()
            if close == message.clickedButton():
                self.seria()
                log_out.close()
                log_err.close()
                event.accept()

            else:
                event.ignore()
        else:
            self.seria()
            log_out.close()
            log_err.close()
            event.accept()

    def add_items_for_combo_box(self):
        self.is_new_building_type.addItems(["Тип квартиры", "Новостройка", "Вторичный"])
        self.room_type.addItems(["Кол-во комнат", "Студия", "1", "2", "3", "4", "5", "6+"])
        self.currency_type.addItems(CURRENCY_CHOISES)
        self.repair_type.addItems([REPAIR_CHOICES_UYBOR[one] for one in REPAIR_CHOICES_UYBOR])

    def update_all_data_clicked(self):
        self.update_uybor_clicked()
        self.update_olx_clicked()

    def update_uybor_clicked(self):
        self.export_button_all_data.setDisabled(True)
        self.export_button_olx.setDisabled(True)

        self.update_uybor.setCheckable(False)
        self.update_uybor.setDisabled(True)
        self.update_all_data.setDisabled(True)
        self.filter_button.setEnabled(True)
        # self.label_progress_bar_uybor.setText("Процесс: Обновление UyBor")
        self.thread_uybor = DataFromDB("uybor", self.rate)
        self.thread_uybor.updated.connect(self.update_uybor_progress_bar)
        self.thread_uybor.throw_exception.connect(self.show_message_with_exit)
        # self.thread_uybor.block_export.connect(self.block)
        self.thread_uybor.block_closing.connect(self.block_close_uybor)
        self.thread_uybor.throw_info.connect(self.show_message_info)
        self.thread_uybor.finished.connect(self.finished_uybor_thread)
        self.thread_uybor.label.connect(self.update_uybor_label)
        self.thread_uybor.date.connect(self.update_date_uybor)
        self.thread_uybor.init_flats.connect(self.update_flats_uybor)
        if not self.uploaded_uybor:
            self.upload_uybor = UploadUybor(self.results_uybor)
            self.upload_uybor.finished.connect(self.upload_uybor_finished)
            self.upload_uybor.start()
            self.uploaded_uybor = True

        self.thread_uybor.start()




    def block_close_uybor(self, block_closing):
        # print(can_be_closed)
        self.can_be_closed[0] = not block_closing

    def block_close_olx(self, block_closing):
        # print(can_be_closed)
        self.can_be_closed[1] = not block_closing

    def block_close_uybor_expot(self, block_closing):
        # print(can_be_closed)
        self.can_be_closed[2] = not block_closing

    def block_close_olx_export(self, block_closing):
        # print(can_be_closed)
        self.can_be_closed[3] = not block_closing

    def block(self, boolen, str_):
        if str_ == "uybor":
            self.export_button_uybor.setDisabled(boolen)
        else:
            self.export_button_olx.setDisabled(boolen)
        if (self.export_button_olx.isEnabled() and
                self.export_button_uybor.isEnabled()):
            self.export_button_all_data.setEnabled(True)

    def finished_uybor_thread(self):
        self.thread_uybor.deleteLater()
        print(f"last update uybor{self.time_last_uybor.toString()}")
        self.update_uybor.setDisabled(False)
        if self.update_olx.isEnabled():
            self.update_all_data.setDisabled(False)
        self.filter_button_clicked()
        self.export_button_uybor.setEnabled(True)

    def show_message_with_exit(self, text):
        self.show_message_info(text)
        sys.exit()

    def show_message_info(self, text):
        self.message.setText(text)
        self.message.setIcon(QMessageBox.Icon.Critical)
        self.message.exec()

    def update_uybor_progress_bar(self, value):
        self.progress_bar_uybor.setProperty("value", value)

    def update_uybor_label(self, value):
        self.label_progress_bar_uybor.setText(f"{value}. Последнее обновление: {self.time_last_uybor.toString()}")

    def update_date_uybor(self, results):
        self.results_uybor = results
        self.time_last_uybor = self.time_last_uybor.currentDateTime(QTimeZone.systemTimeZone())

    def update_flats_uybor(self, results):
        self.results_uybor = results
        self.filter_button_clicked()

    def update_flats_olx(self, results):
        self.results_olx = results
        self.filter_button_clicked()

    # def checker_uybor_finished(self):
    #     time.sleep(60*24)
    #     self.checker_uybor.update_db(self.results_uybor)
    #     self.checker_uybor.start()
    #
    # def checker_olx_finished(self):
    #     time.sleep(60*24)
    #     self.checker_olx.update_db(self.results_olx)


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
        # print(msec / 1000 / 60 / 60)
        self.timer.start(msec)

    def time_update(self):
        print(f"datatime updating start {datetime.datetime.now(tz).time()}")
        self.update_all_data_clicked()
        self.timer.setInterval(24 * 60 * 60 * 1000)

    def update_olx_clicked(self):
        self.export_button_all_data.setDisabled(True)
        self.filter_button.setEnabled(True)
        self.update_all_data.setDisabled(True)
        # self.update_olx.setCheckable(False)
        self.update_olx.setDisabled(True)
        # self.export_button_olx.setDisabled(True)
        self.thread_olx = DataFromDB("olx", self.rate)
        self.thread_olx.updated.connect(self.update_olx_progress_bar)
        self.thread_olx.throw_exception.connect(self.show_message_with_exit)
        self.thread_olx.finished.connect(self.finished_olx_thread)
        # self.thread_olx.block_export.connect(self.block)
        self.thread_olx.date.connect(self.update_date_olx)
        self.thread_olx.label.connect(self.update_olx_label)
        self.thread_olx.block_closing.connect(self.block_close_olx)
        self.thread_olx.throw_info.connect(self.show_message_info)
        self.thread_olx.init_flats.connect(self.update_flats_olx)

        self.thread_olx.start()

    def finished_olx_thread(self):
        self.thread_olx.deleteLater()
        # self.thread_olx.start()
        print(f"last update olx {self.time_last_uybor.toString()}")
        self.update_olx.setDisabled(False)
        self.update_olx.setCheckable(True)
        if self.update_uybor.isEnabled():
            self.update_all_data.setDisabled(False)
        self.filter_button_clicked()
        self.export_button_olx.setEnabled(True)

    def update_olx_label(self, value):
        self.label_progress_bar_olx.setText(f"{value}. Последнее обновление: {self.time_last_olx.toString()}")

    def update_date_olx(self, results):
        self.results_olx = results
        self.time_last_olx = self.time_last_olx.currentDateTime(QTimeZone.systemTimeZone())
        # self.upload_olx = UploadOlx(self.results_olx)
        # self.checker_olx = Checker(self.results_olx)
        # self.checker_olx.finished.connect(self.checker_olx_finished)
        # self.checker_olx.start()
        # self.upload_olx = UploadOlx(self.results_olx)
        # self.upload_olx.finished.connect(self.upload_olx_finished)
        # self.upload_olx.init_update_db.connect(self.answer_to_init_update)
        # self.upload_olx.start()

    def update_olx_progress_bar(self, value):
        self.progress_bar_olx.setProperty("value", value)

    def filter_button_clicked(self):
        # print("1")

        if 'uzs' in self.filters:
            cur = 'uzs'
        else:
            cur = 'uye'
        self.results_uybor_f = filtration(filters=self.filters, results=self.results_uybor)
        self.label_rows_count_uybor.setText(f"Всего строк: {len(self.results_uybor_f)}")
        fill_table_pyqt(self.table_widget_uybor, header, self.results_uybor_f, cur, self.s_, self.f_)
        self.export_button_uybor.setEnabled(len(self.results_uybor_f) > 0)
        self.results_olx_f = filtration(filters=self.filters, results=self.results_olx)
        self.label_rows_count_olx.setText(f"Всего строк: {len(self.results_olx_f)}")
        fill_table_pyqt(self.table_widget_olx, header, self.results_olx_f, cur, self.s_, self.f_)
        self.export_button_olx.setEnabled(len(self.results_olx_f) > 0)
        # self.show_message_info(f"{len(self.results_uybor_f)} + {len(self.results_olx_f)}")
        self.export_button_all_data.setEnabled((len(self.results_uybor_f) * len(self.results_olx_f)) > 0)

    def export_button_clicked_olx(self):
        self.export_button_olx.setCheckable(False)
        self.export_button_olx.setDisabled(True)
        # self.export_button_all_data.setCheckable(False)
        self.export_button_all_data.setDisabled(True)
        self.thread_export_olx = Exporter(name="Olx", results=self.results_olx)
        self.thread_export_olx.throw_exception.connect(self.show_message_with_exit)
        self.thread_export_olx.throw_info.connect(self.show_message_info)
        self.thread_export_olx.finished.connect(self.finised_export_olx)
        self.thread_export_olx.block_closing.connect(self.block_close_olx_export)
        self.thread_export_olx.start()

    def export_button_clicked_uybor(self):
        self.export_button_uybor.setCheckable(False)
        self.export_button_uybor.setDisabled(True)
        self.export_button_all_data.setCheckable(False)
        self.export_button_all_data.setDisabled(True)
        self.thread_export_uybor = Exporter(name="Uybor", results=self.results_uybor)
        self.thread_export_uybor.throw_exception.connect(self.show_message_with_exit)
        self.thread_export_uybor.throw_info.connect(self.show_message_info)
        self.thread_export_uybor.finished.connect(self.finised_export_uybor)
        self.thread_export_uybor.block_closing.connect(self.block_close_uybor_expot)
        self.thread_export_uybor.start()

    def finised_export_olx(self):
        self.thread_export_olx.deleteLater()
        self.export_button_olx.setCheckable(not False)
        self.export_button_olx.setDisabled(not True)
        if (self.export_button_olx.isEnabled() and
                self.export_button_uybor.isEnabled()):
            self.export_button_all_data.setCheckable(not False)
            self.export_button_all_data.setDisabled(not True)

    def finised_export_uybor(self):
        self.thread_export_uybor.deleteLater()
        self.export_button_uybor.setCheckable(True)
        self.export_button_uybor.setEnabled(True)
        if (self.export_button_olx.isEnabled() and
                self.export_button_uybor.isEnabled()):
            self.export_button_all_data.setCheckable(not False)
            self.export_button_all_data.setDisabled(not True)

    def export_button_clicked(self):
        self.export_button_clicked_uybor()
        self.export_button_clicked_olx()

    def cur_chosen(self):
        self.filter_button.setEnabled(True)
        if self.currency_type.currentText() == "СУММ.":
            self.filters.update({"uzs": True})
            self.table_widget_olx.setColumnHidden(11, False)
            self.table_widget_olx.setColumnHidden(10, False)
            self.table_widget_olx.setColumnHidden(8, True)
            self.table_widget_olx.setColumnHidden(9, True)
            self.table_widget_uybor.setColumnHidden(11, False)
            self.table_widget_uybor.setColumnHidden(10, False)
            self.table_widget_uybor.setColumnHidden(8, True)
            self.table_widget_uybor.setColumnHidden(9, True)
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
            if "room" in self.filters:
                self.filters.pop("room")

    def is_new_building_chosen(self):
        self.filter_button.setEnabled(True)
        if self.is_new_building_type.currentText() != "Тип квартиры":
            self.filters.update({"is_new_building": self.is_new_building_type.currentText()})
        else:
            if "is_new_building" in self.filters:
                self.filters.pop("is_new_building")
        time.sleep(1)

    def repair_chosen(self):
        self.filter_button.setEnabled(True)

        if self.repair_type.currentText() != "Ремонт":
            self.filters.update({"repair": self.repair_type.currentText()})
        else:
            if "repair" in self.filters:
                self.filters.pop("repair")

    def price_min_changed(self):
        self.filter_button.setEnabled(True)
        if self.price_min.text() != "":
            self.filters.update({"price_min": int(self.price_min.text())})
        else:
            if "price_min" in self.filters:
                self.filters.pop("price_min")

    def price_max_changed(self):
        self.filter_button.setEnabled(True)
        if self.price_max.text() != "":
            self.filters.update({"price_max": int(self.price_max.text())})
        else:
            if "price_max" in self.filters:
                self.filters.pop("price_max")

    def time_changed(self):
        self.set_time_button.setEnabled(True)
        if self.set_time_input.text() != "":
            self.time_temp = self.set_time_input.time()

    def keyword_changed(self):
        self.filter_button.setEnabled(True)
        if self.keywords.text() != "":
            keywords = self.keywords.text().split(";")
            keywords = [keyword.lower() for keyword in keywords if keyword != '']
            # print(keywords)
            self.filters.update({"keywords": keywords})
        else:
            if "keywords" in self.filters:
                self.filters.pop("keywords")

    def floor_min_changed(self):
        self.filter_button.setCheckable(True)
        if self.floor_min.text() != "":
            self.filters.update({"floor_min": int(self.floor_min.text())})
        else:
            if "floor_min" in self.filters:
                self.filters.pop("floor_min")

    def floor_max_changed(self):
        self.filter_button.setEnabled(True)
        if self.floor_max.text() != "":
            self.filters.update({"floor_max": int(self.floor_max.text())})
        else:
            if "floor_max" in self.filters:
                self.filters.pop("floor_max")

    def square_min_changed(self):
        self.filter_button.setEnabled(True)

        if self.square_min.text() != "":
            self.filters.update({"square_min": float(self.square_min.text())})
        else:
            if "square_min" in self.filters:
                self.filters.pop("square_min")

    def square_max_changed(self):
        self.filter_button.setEnabled(True)

        if self.square_max.text() != "":
            self.filters.update({"square_max": float(self.square_max.text())})
        else:
            if "square_max" in self.filters:
                self.filters.pop("square_max")

    def total_floor_min_changed(self):
        self.filter_button.setEnabled(True)

        if self.total_floor_min.text() != "":
            self.filters.update({"total_floor_min": int(self.total_floor_min.text())})
        else:
            if "total_floor_min" in self.filters:
                self.filters.pop("total_floor_min")

    def total_floor_max_changed(self):
        self.filter_button.setEnabled(True)

        if self.total_floor_max.text() != "":
            self.filters.update({"total_floor_max": int(self.total_floor_max.text())})
        else:
            if "total_floor_max" in self.filters:
                self.filters.pop("total_floor_max")

    def reset_uybor_uploaded_event(self):
        self.uploaded_uybor = False
    # def connect_for_run_olx(self):
    #     print("BLYADINA")
    #     runUploadOlx(self.results_olx)

    def scroll_bar_olx(self):
        if self.table_widget_olx.verticalScrollBar().isSliderDown():
            if self.f_ + 20 < len(self.results_olx_f):
                # self.s_ += 20
                self.f_ += 20
                # print("EPT")
                self.filter_button_clicked()

        if self.table_widget_olx.verticalScrollBar().value() == 0:
            if self.f_ - 20 > 100:
                # self.s_ -= 20
                self.f_ -= 20
                # print("OK EPT")
                self.filter_button_clicked()

    def scroll_bar_uybor(self):
        if self.table_widget_uybor.verticalScrollBar().isSliderDown():
            if self.f_ + 20 < len(self.results_olx_f):
                # self.s_ += 20
                self.f_ += 20
                # print("EPT")
                self.filter_button_clicked()

        if self.table_widget_uybor.verticalScrollBar().value() == 0:
            if self.f_ - 20 > 100:
                # self.s_ -= 20
                self.f_ -= 20
                # print("OK EPT")
                self.filter_button_clicked()

    def handler(self):
        self.timer_reset_uybor_uploaded = QtCore.QTimer()
        self.timer_reset_uybor_uploaded.timeout.connect(self.reset_uybor_uploaded_event)
        self.timer_reset_uybor_uploaded.start(1000 * 60 * 60)
        self.upload_olx = UploadOlx(self.results_olx)
        self.upload_olx.finished.connect(self.upload_olx_finished)
        self.upload_olx.init_update_db.connect(self.answer_to_init_update)
        self.upload_olx.start()
        # self.table_widget_uybor.verticalScrollBar().valueChanged.connect()
        self.table_widget_olx.verticalScrollBar().valueChanged.connect(self.scroll_bar_olx)
        self.table_widget_uybor.verticalScrollBar().valueChanged.connect(self.scroll_bar_uybor)

        self.set_time_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.set_time_button.clicked.connect(self.time_clicked)
        self.room_type.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.repair_type.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.currency_type.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.is_new_building_type.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.progress_bar_uybor.setCursor(QCursor(Qt.CursorShape.BusyCursor))
        self.progress_bar_olx.setCursor(QCursor(Qt.CursorShape.BusyCursor))

        self.room_type.activated.connect(self.room_chosen)
        self.repair_type.activated.connect(self.repair_chosen)
        self.currency_type.activated.connect(self.cur_chosen)
        self.is_new_building_type.activated.connect(self.is_new_building_chosen)
        self.export_button_olx.setCheckable(True)

        self.export_button_uybor.setCheckable(True)

        self.export_button_olx.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.export_button_uybor.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.export_button_all_data.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.export_button_olx.clicked.connect(self.export_button_clicked_olx)
        self.export_button_uybor.clicked.connect(self.export_button_clicked_uybor)
        self.export_button_all_data.clicked.connect(self.export_button_clicked)

        self.update_all_data.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.update_all_data.clicked.connect(self.update_all_data_clicked)
        self.update_olx.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.update_olx.clicked.connect(self.update_olx_clicked)
        self.update_uybor.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.update_uybor.clicked.connect(self.update_uybor_clicked)
        self.filter_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.filter_button.clicked.connect(self.filter_button_clicked)
        self.price_min.textChanged.connect(self.price_min_changed)
        self.price_max.textChanged.connect(self.price_max_changed)
        self.square_min.textChanged.connect(self.square_min_changed)
        self.square_max.textChanged.connect(self.square_max_changed)
        self.floor_min.textChanged.connect(self.floor_min_changed)
        self.floor_max.textChanged.connect(self.floor_max_changed)
        self.keywords.textChanged.connect(self.keyword_changed)
        self.total_floor_max.textChanged.connect(self.total_floor_max_changed)
        self.total_floor_min.textChanged.connect(self.total_floor_min_changed)
        self.set_time_input.timeChanged.connect(self.time_changed)

    def upload_uybor_finished(self):
        # time.sleep(60*24)

        # self.upload_uybor.update_db(self.results_uybor)
        self.upload_uybor.deleteLater()
        self.uploaded_uybor = True
        self.update_uybor_clicked()

    def answer_to_init_update(self):
        # self.update_olx_clicked()
        print("init to olx update")
        self.upload_olx.update_db(self.results_olx)

    def upload_olx_finished(self):
        # time.sleep(60*24)
        self.upload_olx.update_db(self.results_uybor)
        self.upload_olx.deleteLater()
        self.update_olx_clicked()



if not os.path.exists("_internal/output"):
    os.mkdir("_internal/output")
log_out = open('_internal/output/log_out.txt', 'a', encoding="utf-8")
log_err = open('_internal/output/log_err.txt', 'a', encoding="utf-8")


if __name__ == "__main__":
    sys.stdout = log_out
    sys.stderr = log_err
    app = QtWidgets.QApplication(sys.argv)
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
        log_err.close()

