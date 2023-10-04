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


def header_sheet(sheet):
    header = [
        "цена, $",
        "цена за метр, $",
        "цена, сумм",
        "цена за метр, сумм",
        "мерты",
        "этаж",
        "address",
        "ремонт",
        "новостройка",
        'кол-во комнаты',
        "ссылка",
        "дата обновления",
    ]
    for i in range(len(header)):
        sheet.write(0, i, header[i])


def fill_sheet_uybor(sheet):
    # header_sheet(sheet)
    delta = 1
    page = 0
    while True:
        results = json_uybor(page)
        if len(results) == 0:
            return
        for i in range(len(results)):
            sheet.write(i + delta, 0, results[i]['prices']['usd'])
            sheet.write(i + delta, 1, results[i]['prices']['usd'] / results[i]['square'])
            sheet.write(i + delta, 2, results[i]['prices']['uzs'])
            sheet.write(i + delta, 3, results[i]['prices']['uzs'] / results[i]['square'])
            sheet.write(i + delta, 4, f"{results[i]['square']}")
            sheet.write(i + delta, 5, f'{results[i]["floor"]}/{results[i]["floorTotal"]}')
            address = ''
            if results[i]['zone'] is not None:
                address += results[i]['zone']['name']['ru']
            if results[i]['region'] is not None:
                address += ' ' + results[i]['region']['name']['ru']
            if results[i]['cityId'] is not None:
                address += ' ' + results[i]['city']['name']['ru']
            if results[i]['district'] is not None:
                address += ' ' + results[i]['district']['name']['ru']
            if results[i]['metro'] is not None:
                address += ' ' + results[i]['metro']['name']['ru']
            if results[i]['residentialComplex'] is not None:
                address += ' ' + results[i]['residentialComplex']['name']['ru']
            if results[i]['address'] is not None:
                address += ' ' + results[i]['address']
                sheet.write(i + delta, 6, address)
            if results[i]['repair'] is not None:
                sheet.write(i + delta, 7, REPAIR_CHOICES_UYBOR[results[i]['repair']])
            if results[i]['isNewBuilding']:
                sheet.write(i + delta, 8, 'Новостройка')
            else:
                sheet.write(i + delta, 8, 'Вторичка')
            sheet.write(i + delta, 9, results[i]['room'])
            sheet.write(i + delta, 10, f'https://uybor.uz/listings/{results[i]["id"]}')
            sheet.write(i + delta, 11, results[i]['updatedAt'])
        delta += len(results)
        page += 1
        results.clear()
        return



