import datetime
import os
import time
import xlwt
from olx_parsing import fill_sheet_olx
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
    start = time.time()
    excel(
        f"output/uybor{datetime.datetime.now().strftime('%d%m%y_%H%M')}",
        fill_sheet=fill_sheet_uybor
    )
    print(time.time() - start)
    start = time.time()
    excel(
        f"output/olx{datetime.datetime.now().strftime('%d%m%y_%H%M')}",
        fill_sheet=fill_sheet_olx
    )
    print(time.time() - start)

