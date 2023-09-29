import requests


REPAIR_CHOICES_UYBOR = {
    "evro": "Евроремонт",
    "custom": "Авторский",
    "sredniy": "Средний",
    "kapital": "Требует ремонта",
    "chernovaya": "Черновая отделка"
}


def json_uybor(page=0, limit=100):
    # усл ед "usd"
    # суммы "uzs"
    url = "https://api.uybor.uz/api/v1/listings"
    params = {
        "limit": limit,
        "page": page,
        "mode": "search",
        "order": "upAt",
        "embed": "category,residentialComplex,region,city,district,zone,street,metro",
        "operationType__eq": "sale",
        "category__eq": "7"
    }
    request = requests.get(url, params).json()
    return request["results"]


def fill_sheet_uybor(sheets):
    cur = ['usd', 'uzs']
    header = [
        "цена",
        "цена за метр",
        "мерты",
        "этаж",
        # "zone",
        "address",
        # "region",
        # "city",
        # "district",
        # "metro",
        # 'residentialComplex',
        'кол - во комнаты',
        "ремонт",
        "тип жилья",
        "ссылка",
        "дата обновления",

    ]
    for i in range(len(header)):
        for sheet in sheets:
            sheet.write(0, i, header[i])
    delta = 1
    page = 0
    while True:
        results = json_uybor(page)
        if len(results) == 0:
            return
        for i in range(len(results)):
            for sheet in sheets:
                sheet.write(i + delta, 0, results[i]['prices'][cur[sheets.index(sheet)]])
                sheet.write(i + delta, 1, results[i]['prices'][cur[sheets.index(sheet)]] / results[i]['square'])
                sheet.write(i + delta, 2, f"{results[i]['square']}")
                sheet.write(i + delta, 3, f'{results[i]["floor"]}/{results[i]["floorTotal"]}')
                if results[i]['address'] is not None:
                    address = ''
                    if results[i]['zone'] is not None:
                        address = address + results[i]['zone']['name']['ru'] + ', '
                    if results[i]['region'] is not None:
                        address = address + results[i]['region']['name']['ru'] + ', '
                    if results[i]['cityId'] is not None:
                        address = address + results[i]['city']['name']['ru'] + ', '
                    if results[i]['district'] is not None:
                        address = address + results[i]['district']['name']['ru'] + ', '
                    if results[i]['metro'] is not None:
                        address = address + results[i]['metro']['name']['ru'] + ', '
                    if results[i]['residentialComplex'] is not None:
                        address = address + results[i]['residentialComplex']['name']['ru'] + ', '
                    address = address + results[i]['address']
                    sheet.write(i + delta, 4, address)
                sheet.write(i + delta, 5, results[i]['room'])
                if results[i]['repair'] is not None:
                    sheet.write(i + delta, 11, REPAIR_CHOICES_UYBOR[results[i]['repair']])
                if results[i]['isNewBuilding']:
                    sheet.write(i + delta, 12, 'Новостройка')
                else:
                    sheet.write(i + delta, 12, 'Вторичка')
                sheet.write(i + delta, 13, f'https://uybor.uz/listings/{results[i]["id"]}')
                sheet.write(i + delta, 14, results[i]['updatedAt'])
        delta += len(results)
        page += 1
        results.clear()



