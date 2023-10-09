import os
from openpyxl import load_workbook
from olx_parsing import Flat


def get_arr_from_excel(name):

    input_book = load_workbook(name)
    ws_input_book = input_book[input_book.sheetnames[0]]
    flats = []
    for row in ws_input_book.iter_rows(min_row=2, max_col=12):
        flats.append(Flat(
            price_uye=float(row[0].value),
            price_uzs=float(row[2].value),
            square=  row[4].value,  # TODO FIX TYPES float(row[4].value),
            address=row[6].value,
            repair=row[7].value,
            is_new_building=row[8].value,
            room=row[9].value,
            url=row[10].value,
            modified=row[11].value,
            floor=int(row[5].value.split("/")[0]),
            total_floor=int(row[5].value.split("/")[1])))
    return flats


# TODO проверки на существования файла

def filter(filters, resource):
    # if os.path.exists(filters['resource']):
    #     results = get_arr_from_excel(filters['resource'])
    # else:
    #     print("Необходимо выгрузить данные")
    results = get_arr_from_excel(resource)
    # print(len(results))
    if 'price_min' in filters:
        if 'uzs' in filters:
            results = [result for result in results if result.price_uzs >= filters['price_min']]
        if 'uye' in filters:
            results = [result for result in results if result.price_uye >= filters['price_min']]
    # print(len(results))
    if 'price_max' in filters:
        if 'uzs' in filters:
            results = [result for result in results if result.price_uzs <= filters['price_max']]
        if 'uye' in filters:
            results = [result for result in results if result.price_uye <= filters['price_max']]
    # print(len(results))
    if 'is_new_building' in filters:
        results = [result for result in results if result.is_new_building == filters['is_new_building']]
    # print(len(results))
    if 'repair' in filters:
        results = [result for result in results if result.repair == filters['repair']]
    # print(len(results))
    if 'room' in filters:
        results = [result for result in results if result.room == filters['room']]
    # print(len(results))
    if 'square_min' in filters:
        results = [result for result in results if result.square >= filters['square_min']]
    # print(len(results))
    if 'square_max' in filters:
        results = [result for result in results if result.square <= filters['square_max']]
    # print(len(results))
    if 'floor_min' in filters:
        results = [result for result in results if result.floor >= filters['floor_min']]
    # print(len(results))
    if 'floor_max' in filters:
        results = [result for result in results if int(result.floor) <= int(filters['floor_max'])]
    # print(len(results))
    return results


def fill_filtered_data(sheet, results):
    # sheet.append(get_arr_from_excel(filters['resourse']))  # path to resourse excel file
    # results = filter(filters)
    if len(results) == 0:
        print("НЕТ ЭЛЕМЕНТОВ В ВЫБОРКЕ")
        return None
    for i in range(0, len(results)):
        sheet.append([results[i].price_uye,
                      results[i].price_per_meter_uye,
                      results[i].price_uzs,
                      results[i].price_per_meter_uzs,
                      results[i].square,
                      f'{results[i].floor}/{results[i].total_floor}',
                      results[i].address,
                      results[i].repair,
                      results[i].is_new_building,
                      results[i].room,
                      results[i].url,
                      results[i].modified])
