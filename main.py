import datetime
import os
import xlwt
from uybor_api import fill_sheet_uybor


def excel(name_of_file, fill_sheet):
    book_uybor = xlwt.Workbook(encoding="utf-8")
    fill_sheet([book_uybor.add_sheet("У.Е"), book_uybor.add_sheet("СУММ")])
    if os.path.exists(f"{name_of_file}.xls"):
        os.remove(f"{name_of_file}.xls")
    book_uybor.save(f"{name_of_file}.xls")


if __name__ == "__main__":
    if not os.path.exists("output/"):
        os.mkdir("output")
    excel(
        f"output/uybor{datetime.datetime.now().strftime('%d%m%y_%H%M')}",
          fill_sheet=fill_sheet_uybor
    )
    # url = "https://www.olx.uz/nedvizhimost/kvartiry/prodazha/"

