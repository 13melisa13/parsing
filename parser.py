# Form implementation generated from reading ui file 'parser.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.
import os
import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from main import create_internal_excel_file, create_filtered_excel_file
from olx_parsing import fill_sheet_olx
from uybor_api import fill_sheet_uybor
from filtr_excel import filter, fill_filtered_data


def update_uybor_clicked():
    print("start_create_internal_uybor")
    create_internal_excel_file("uybor", fill_sheet_uybor)
    print("finished_create_internal_uybor")


def update_olx_clicked():
    print("start_create_internal_olx")
    create_internal_excel_file("olx", fill_sheet_olx)
    print("finished_create_internal_olx")


def update_all_data_clicked():
    update_uybor_clicked()
    update_olx_clicked()


class Ui_Parser(object):
    results_olx = []
    results_uybor = []
    filters = {}

    def filter_button_clicked(self):
        print("start_filtering_olx")
        self.results_olx = filter(filters=self.filters, resource="output/internal/olx.xlsm")
        print(len(self.results_olx))
        print("start_filtering_uybor")

        self.results_uybor = filter(filters=self.filters, resource="output/internal/uybor.xlsm")
        print(len(self.results_uybor))

    def export_button_clicked(self):
        create_filtered_excel_file(fill_filtered_data, "olx",  self.results_olx)
        create_filtered_excel_file(fill_filtered_data, "uybor",  self.results_olx)


    def setupUi(self, Parser):
        Parser.setObjectName("Parser")
        Parser.resize(1061, 751)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Parser.sizePolicy().hasHeightForWidth())
        Parser.setSizePolicy(sizePolicy)
        Parser.setMinimumSize(QtCore.QSize(1061, 751))
        Parser.setMaximumSize(QtCore.QSize(1061, 751))
        Parser.setAutoFillBackground(True)

        self.main_widget = QtWidgets.QWidget(parent=Parser)
        self.main_widget.setObjectName("main_widget")
        self.FilterFrame = QtWidgets.QFrame(parent=self.main_widget)
        self.FilterFrame.setGeometry(QtCore.QRect(10, 130, 1041, 51))
        self.FilterFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.FilterFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.FilterFrame.setObjectName("FilterFrame")
        self.label_3 = QtWidgets.QLabel(parent=self.FilterFrame)
        self.label_3.setGeometry(QtCore.QRect(320, 0, 47, 13))
        self.label_3.setObjectName("label_3")
        self.min_worth = QtWidgets.QLineEdit(parent=self.FilterFrame)
        self.min_worth.setGeometry(QtCore.QRect(70, 20, 121, 21))
        self.min_worth.setObjectName("min_worth")
        self.label_2 = QtWidgets.QLabel(parent=self.FilterFrame)
        self.label_2.setGeometry(QtCore.QRect(480, 0, 47, 13))
        self.label_2.setObjectName("label_2")
        self.type = QtWidgets.QComboBox(parent=self.FilterFrame)
        self.type.setGeometry(QtCore.QRect(600, 10, 151, 41))
        self.type.setObjectName("type")
        self.min_floor = QtWidgets.QLineEdit(parent=self.FilterFrame)
        self.min_floor.setGeometry(QtCore.QRect(320, 20, 31, 21))
        self.min_floor.setObjectName("min_floor")
        self.max_floor = QtWidgets.QLineEdit(parent=self.FilterFrame)
        self.max_floor.setGeometry(QtCore.QRect(360, 20, 31, 21))
        self.max_floor.setObjectName("max_floor")
        self.label_4 = QtWidgets.QLabel(parent=self.FilterFrame)
        self.label_4.setGeometry(QtCore.QRect(390, -4, 81, 20))
        self.label_4.setObjectName("label_4")
        self.max_worth = QtWidgets.QLineEdit(parent=self.FilterFrame)
        self.max_worth.setGeometry(QtCore.QRect(200, 20, 111, 21))
        self.max_worth.setObjectName("max_worth")
        self.max_room_count = QtWidgets.QLineEdit(parent=self.FilterFrame)
        self.max_room_count.setGeometry(QtCore.QRect(440, 20, 31, 21))
        self.max_room_count.setObjectName("max_room_count")
        self.min_room_count = QtWidgets.QLineEdit(parent=self.FilterFrame)
        self.min_room_count.setGeometry(QtCore.QRect(400, 20, 31, 21))
        self.min_room_count.setObjectName("min_room_count")
        self.label = QtWidgets.QLabel(parent=self.FilterFrame)
        self.label.setGeometry(QtCore.QRect(10, 0, 47, 13))
        self.label.setObjectName("label")
        self.max_square = QtWidgets.QLineEdit(parent=self.FilterFrame)
        self.max_square.setGeometry(QtCore.QRect(540, 20, 51, 21))
        self.max_square.setObjectName("max_square")
        self.min_square = QtWidgets.QLineEdit(parent=self.FilterFrame)
        self.min_square.setGeometry(QtCore.QRect(480, 20, 51, 21))
        self.min_square.setObjectName("min_square")

        self.filter_button = QtWidgets.QPushButton(parent=self.FilterFrame)
        self.filter_button.setGeometry(QtCore.QRect(920, 20, 111, 21))


        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ToolTipText, brush)


        self.filter_button.setPalette(palette)
        self.filter_button.setAutoFillBackground(False)
        self.filter_button.setObjectName("filter_button")
        self.filter_button.setCheckable(True)
        self.filter_button.clicked.connect(self.filter_button_clicked)

        self.currency = QtWidgets.QComboBox(parent=self.FilterFrame)
        self.currency.setGeometry(QtCore.QRect(0, 20, 61, 21))
        self.currency.setObjectName("currency")



        self.repair_type = QtWidgets.QComboBox(parent=self.FilterFrame)
        self.repair_type.setGeometry(QtCore.QRect(760, 10, 151, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ToolTipText, brush)
        self.repair_type.setPalette(palette)
        self.repair_type.setObjectName("repair_type")
        self.ProcessBarFrame = QtWidgets.QFrame(parent=self.main_widget)
        self.ProcessBarFrame.setGeometry(QtCore.QRect(10, 50, 1051, 80))
        self.ProcessBarFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.ProcessBarFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.ProcessBarFrame.setObjectName("ProcessBarFrame")
        self.label_6 = QtWidgets.QLabel(parent=self.ProcessBarFrame)
        self.label_6.setGeometry(QtCore.QRect(0, 16, 41, 20))
        self.label_6.setObjectName("label_6")
        self.process_name_label = QtWidgets.QLabel(parent=self.ProcessBarFrame)
        self.process_name_label.setGeometry(QtCore.QRect(50, 16, 931, 20))
        self.process_name_label.setObjectName("process_name_label")

        self.progressBar = QtWidgets.QProgressBar(parent=self.ProcessBarFrame)
        self.progressBar.setGeometry(QtCore.QRect(0, 40, 1041, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")


        self.StatsFrame = QtWidgets.QFrame(parent=self.main_widget)
        self.StatsFrame.setGeometry(QtCore.QRect(10, 720, 1041, 41))
        self.StatsFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.StatsFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.StatsFrame.setObjectName("StatsFrame")
        self.rows_count = QtWidgets.QLCDNumber(parent=self.StatsFrame)
        self.rows_count.setGeometry(QtCore.QRect(80, 0, 91, 23))
        self.rows_count.setObjectName("rows_count")
        self.label_5 = QtWidgets.QLabel(parent=self.StatsFrame)
        self.label_5.setGeometry(QtCore.QRect(10, 0, 71, 21))
        self.label_5.setObjectName("label_5")
        self.MainFunctionsFrame = QtWidgets.QFrame(parent=self.main_widget)
        self.MainFunctionsFrame.setGeometry(QtCore.QRect(10, 0, 1041, 51))
        self.MainFunctionsFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.MainFunctionsFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.MainFunctionsFrame.setObjectName("MainFunctionsFrame")

        self.update_olx = QtWidgets.QPushButton(parent=self.MainFunctionsFrame)
        self.update_olx.setCheckable(True)
        self.update_olx.clicked.connect(update_olx_clicked)
        self.update_olx.setGeometry(QtCore.QRect(450, 10, 141, 31))
        self.update_olx.setObjectName("update_olx")

        self.update_uybor = QtWidgets.QPushButton(parent=self.MainFunctionsFrame)
        self.update_uybor.setCheckable(True)
        self.update_uybor.clicked.connect(update_uybor_clicked)
        self.update_uybor.setGeometry(QtCore.QRect(300, 10, 141, 31))
        self.update_uybor.setObjectName("update_uybor")

        self.update_all_data = QtWidgets.QPushButton(parent=self.MainFunctionsFrame)
        self.update_all_data.setCheckable(True)
        self.update_all_data.clicked.connect(update_all_data_clicked)
        self.update_all_data.setGeometry(QtCore.QRect(150, 10, 141, 31))
        self.update_all_data.setObjectName("update_all_data")


        self.export_button = QtWidgets.QPushButton(parent=self.MainFunctionsFrame)
        self.export_button.setCheckable(True)
        self.export_button.clicked.connect(self.export_button_clicked)
        self.export_button.setGeometry(QtCore.QRect(0, 10, 141, 31))
        self.export_button.setObjectName("export_button")


        self.label_7 = QtWidgets.QLabel(parent=self.main_widget)
        self.label_7.setGeometry(QtCore.QRect(10, 200, 81, 16))
        self.label_7.setObjectName("label_7")
        self.DataView = QtWidgets.QTabWidget(parent=self.main_widget)
        self.DataView.setGeometry(QtCore.QRect(10, 220, 1041, 501))
        self.DataView.setObjectName("DataView")
        self.UyBor = QtWidgets.QWidget()
        self.UyBor.setObjectName("UyBor")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.UyBor)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tableWidget = QtWidgets.QTableWidget(parent=self.UyBor)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.horizontalLayout_2.addWidget(self.tableWidget)
        self.DataView.addTab(self.UyBor, "")
        self.Olx = QtWidgets.QWidget()
        self.Olx.setObjectName("Olx")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.Olx)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tableWidget_2 = QtWidgets.QTableWidget(parent=self.Olx)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.horizontalLayout_3.addWidget(self.tableWidget_2)
        self.DataView.addTab(self.Olx, "")
        self.StatsFrame.raise_()
        self.ProcessBarFrame.raise_()
        self.FilterFrame.raise_()
        self.MainFunctionsFrame.raise_()
        self.label_7.raise_()
        self.DataView.raise_()
        Parser.setCentralWidget(self.main_widget)

        self.retranslateUi(Parser)
        self.DataView.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Parser)

    def retranslateUi(self, Parser):
        _translate = QtCore.QCoreApplication.translate
        Parser.setWindowTitle(_translate("Parser", "MAEParser"))
        self.label_3.setText(_translate("Parser", "Этаж"))
        self.label_2.setText(_translate("Parser", "Площадь"))
        self.label_4.setText(_translate("Parser", "Кол-во комнат"))
        self.label.setText(_translate("Parser", "Цена"))
        self.filter_button.setText(_translate("Parser", "Отфильтровать"))
        self.label_6.setText(_translate("Parser", "Процес:"))
        self.process_name_label.setText(_translate("Parser", "ProcessName"))
        self.label_5.setText(_translate("Parser", "Всего строк:"))
        self.update_olx.setText(_translate("Parser", "Обновить Olx"))
        self.update_uybor.setText(_translate("Parser", "Обновить UyBor"))
        self.update_all_data.setText(_translate("Parser", "Обновить данные"))
        self.export_button.setText(_translate("Parser", "Экспортировать в xlsm"))
        self.label_7.setText(_translate("Parser", "Предпросмотр"))
        self.DataView.setTabText(self.DataView.indexOf(self.UyBor), _translate("Parser", "UyBor"))
        self.DataView.setTabText(self.DataView.indexOf(self.Olx), _translate("Parser", "Olx"))


if __name__ == "__main__":

    if not os.path.exists("output"):
        os.mkdir("output")
    if not os.path.exists("output/internal"):
        os.mkdir("output/internal")
    app = QtWidgets.QApplication(sys.argv)
    Parser = QtWidgets.QMainWindow()
    ui = Ui_Parser()
    ui.setupUi(Parser)
    Parser.show()
    sys.exit(app.exec())
    # app.exec()