import datetime
import os
import time
import xlwt
from olx_parsing import fill_sheet_olx
from uybor_api import fill_sheet_uybor


def excel(name_of_file):
    book = xlwt.Workbook(encoding="utf-8")
    fill_sheet_uybor([book.add_sheet("uybor У.Е"),
                      book.add_sheet("uybor СУММ")])
    fill_sheet_olx([book.add_sheet("olx У.Е"),
                    book.add_sheet("olx СУММ")])
    if os.path.exists(f"{name_of_file}.xls"):
        os.remove(f"{name_of_file}.xls")
    book.save(f"{name_of_file}.xls")


if __name__ == "__main__":
    if not os.path.exists("output/"):
        os.mkdir("output")
    excel(f"output/{datetime.datetime.now().strftime('%d%m%y_%H%M')}")

