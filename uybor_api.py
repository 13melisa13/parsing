import requests


REPAIR_CHOICES_UYBOR = {
    "evro": "Евроремонт",
    "custom": "Авторский проект",
    "sredniy": "Средний",
    "kapital": "Требует ремонта",
    "chernovaya": "Черновая отделка",
    "predchistovaya": "Предчистовая отделка"
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
    sheet.append([
        "цена, $",
        "цена за метр, $",
        "цена, сумм",
        "цена за метр, сумм",
        "мерты",
        "этаж",
        "адрес",
        "ремонт",
        "новостройка",
        'кол-во комнат',
        "ссылка",
        "дата обновления",
    ])


def fill_sheet_uybor(sheet, agrs=[]):
    # header_sheet(sheet)
    page = 0
    while True:
        # print("start")
        results = json_uybor(page)
        if len(results) == 0:
            return
        for i in range(len(results)):
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
            if results[i]['repair'] is not None:
                repair = REPAIR_CHOICES_UYBOR[results[i]['repair']]
            else:
                repair = ''
            if results[i]['isNewBuilding']:
                is_new_building = 'Новостройка'
            else:
                is_new_building = 'Вторичка'
            if not isinstance(results[i]['room'], int):
                room = results[i]['room']
            else:
                if results[i]['room'] == 'freeLayout':
                    room = 'Студия'
            row = (
                    results[i]['prices']['usd'],
                    results[i]['prices']['usd'] / results[i]['square'],
                    results[i]['prices']['uzs'],
                    results[i]['prices']['uzs'] / results[i]['square'],
                    int(results[i]['square']),
                    f'{results[i]["floor"]}/{results[i]["floorTotal"]}',
                    address,
                    repair,
                    is_new_building,
                    room,
                    f'https://uybor.uz/listings/{results[i]["id"]}',
                    results[i]['updatedAt']
            )
            sheet.append(row)
            # print(address)
        return
        page += 1




