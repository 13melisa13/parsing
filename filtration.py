def filtration_lands(filters, results): #todo
    return results


def filtration_commerces(filters, results): #todo
    return results


def filtration(filters, results, type_of_re): # todo splito to nedvizh, flat and other
    print(f"filters: {filters}")
    # print(len(results))
    if 'price_min' in filters:
        if 'uzs' in filters:
            results = [result for result in results if float(result.price_uzs) >= filters['price_min']]
        if 'uye' in filters:
            results = [result for result in results if float(result.price_uye) >= filters['price_min']]
    # print(len(results))
    if 'price_max' in filters:
        if 'uzs' in filters:
            results = [result for result in results if float(result.price_uzs) <= filters['price_max']]
        if 'uye' in filters:
            results = [result for result in results if float(result.price_uye) <= filters['price_max']]
    # print(len(results))

    # print(len(results))
    if 'square_min' in filters:
        results = [result for result in results if float(result.square) >= filters['square_min']]
    # print(len(results))
    if 'square_max' in filters:
        results = [result for result in results if float(result.square) <= filters['square_max']]
    # print(len(results))

    if 'keywords' in filters:
        old = results
        results = []
        for result in old:
            for keyword in filters['keywords']:
                if keyword in (result.description.lower() + result.address.lower()) and result not in results:
                    results.append(result)
                    # print(result.url)
    match type_of_re:
        case 'flat':
            results = filtration_flats(filters, results)
        case 'land':
            results = filtration_lands(filters, results)
        case 'commerce':
            results = filtration_commerces(filters, results)

    return results



def filtration_flats(filters,results):
    if 'floor_min' in filters:
        results = [result for result in results if int(result.floor) <= int(filters['floor_min'])]
    # print(len(results))
    if 'floor_max' in filters:
        results = [result for result in results if int(result.floor) <= int(filters['floor_max'])]
    # print(len(results))
    if 'total_floor_min' in filters:
        results = [result for result in results if int(result.total_floor) >= filters['total_floor_min']]
    # print(len(results))
    if 'total_floor_max' in filters:
        results = [result for result in results if int(result.total_floor) <= int(filters['total_floor_max'])]
    # print(len(results))
    if 'repair' in filters and filters['repair'] != "Не выбрано":
        results = [result for result in results if result.repair == filters['repair']]
    # print(len(results))
    if 'room' in filters and filters['room'] != "Не выбрано":
        results = [result for result in results if result.room == filters['room']]
    # print(len(results))
    if 'is_new_building' in filters and filters['is_new_building'] != "Не выбрано":
        new_res = []
        for result in results:
            if filters['is_new_building'] == 'Вторичный':
                if result.is_new_building == filters['is_new_building']:
                    new_res.append(result)
            else:
                if result.is_new_building == 'Новостройка' or result.is_new_building == 'Новостройки':
                    new_res.append(result)
        results = new_res
    return results

