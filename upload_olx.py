import asyncio
import random
import sys
import time
import aiohttp
from aiohttp.client_exceptions import ClientOSError, ClientPayloadError
from datetime import datetime

from flat import Flat

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.170",
    "accept": "*/*"
}

# todo def create_param_combos():


async def get_offers(url=None, **params):
    session_timeout = aiohttp.ClientTimeout(total=None)
    session = aiohttp.ClientSession(headers=headers, timeout=session_timeout)
    responses = {}
    if url:
        async with session.get(url) as resp:
            if resp.status == 200:
                responses = await resp.json()
    else:
        params['category_id'] = 13
        if 'limit' not in params.keys():
            params['limit'] = 50
        if 'offset' not in params.keys():
            params['offset'] = 0
        if 'currency' not in params.keys():
            params['currency'] = random.choice(['UZS', 'UYE'])
        if 'filter_enum_type_of_market' not in params.keys():
            params['filter_enum_type_of_market'] = random.choice(['secondary', 'primary', 'secondary,primary'])
        if 'filter_enum_comission' not in params.keys():
            params['filter_enum_comission'] = random.choice(['yes', 'no', 'yes,no'])
        if 'filter_enum_furnished' not in params.keys():
            params['filter_enum_furnished'] = random.choice(['yes', 'no', 'yes,no'])
        if random.choice([True, False, False]) and 'filter_enum_repairs' not in params.keys():
            params['filter_enum_repairs'] = random.randint(1, 6)
        if random.choice([True, False, False]) and 'filter_float_floor:from' not in params.keys():
            params['filter_float_floor:from'] = float(random.randint(1, 20))
        if random.choice([True, False, False]) and 'filter_float_floor:to' not in params.keys():
            params['filter_float_floor:to'] = float(random.randint(1, 100))
        if random.choice([True, False, False]) and 'filter_float_total_area:from' not in params.keys():
            params['filter_float_total_area:from'] = float(random.randint(1, 100))
        elif random.choice([True, False, False]) and 'filter_float_total_area:from' not in params.keys():
            params['filter_float_total_area:to'] = float(random.randint(1, 10000))
        if random.choice([True, False, False]) and 'filter_float_price:from' not in params.keys():
            params['filter_float_price:from'] = random.randint(0, 10000000)
        elif random.choice([True, False, False]) and 'filter_float_price:to' not in params.keys():
            params['filter_float_price:to'] = random.randint(0, 10000000)
        if random.choice([True, False, False]) and 'filter_float_number_of_rooms:from' not in params.keys():
            params['filter_float_number_of_rooms:from'] = float(random.randint(1, 6))
        elif random.choice([True, False, False]) and 'filter_float_number_of_rooms:to' not in params.keys():
            params['filter_float_number_of_rooms:to'] = float(random.randint(1, 10))

        sort = ['created_at:desc',
                'filter_float_price:desc',
                'relevance:desc',
                'filter_float_price:asc']
        response = []
        for sort_one in sort:
            params['sort_by'] = sort_one
            print(params)
            delay = random.randint(1, 5)
            print("Delay of first:", delay)
            time.sleep(delay)
            async with session.get('https://www.olx.uz/api/v1/offers/', params=params) as resp:
                if resp.status == 200:
                    # print(len(response))
                    r = await resp.json(encoding="utf-8")
                    # print(r)
                    response.append(r)
                    responses = {"responses": response}
    await session.close()
    return responses


async def start_olx_polling():
    while True:
        start = datetime.now()
        total_elements = []
        try:
            resp = await get_offers()
        except (ClientOSError, ClientPayloadError) as er:
            await asyncio.sleep(10)
            print(er)
            continue
        responses = resp.get("responses")
        print(len(responses))
        for response in responses:
            new_offers = [one.get('id') for one in response.get('data')]
            meta = response.get('metadata')
            total_elements.append(meta.get('visible_total_count'))
            print(responses.index(response), meta.get('visible_total_count'))

            # # db_offers = get_offers_from_db_all(url_db, "olx", 50)
            # db_offers.extend([one_offers for one_offers in new_offers if one_offers not in db_offers])
            next_page = response.get('links', {}).get('next', {}).get('href')
            while next_page:
                try:
                    resp1 = await get_offers(next_page)
                except ClientOSError as er:
                    await asyncio.sleep(10)
                    print(er)
                    break
                new_offers = [one.get('id') for one in resp1.get('data')]
                db_offers.extend([one_offers for one_offers in new_offers if one_offers not in db_offers])
                next_page = resp1.get('links', {}).get('next', {}).get('href')
        print()
        print('Cycle duration: ', f'{(datetime.now() - start).total_seconds() :.3f}s', )
        print('Time from start: ', f'{(datetime.now() - start_main).total_seconds() :.3f}s',
              f'{len(db_offers)}/ {total_elements}')
        # print(len([item for item in db_offers if db_offers.count(item) > 1]))
        delay = random.randint(0, 10)
        print("Delay: ", delay)
        time.sleep(delay)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(start_olx_polling())
