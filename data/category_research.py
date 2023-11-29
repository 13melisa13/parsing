import asyncio
import random

import aiohttp

from models import headers


async def get_cat():
    for i in range(0, 2000):
        params = {'category_id': i}
        session_timeout = aiohttp.ClientTimeout(total=None)
        session = aiohttp.ClientSession(headers=headers, timeout=session_timeout)
        async with (session.get('https://www.olx.uz/api/v1/offers/', params=params) as resp):
            if resp.status == 200:
                r = (await resp.json()).get('metadata').get('adverts').get('config').get('targeting')
                if "Недвижимость" == r.get('cat_l0_name') or "Недвижимость" == r.get('cat_l1_name') or "Недвижимость" == r.get('cat_l1_name'):
                    print(i, r.get('cat_l0_name'), r.get('cat_l2_name'), r.get('cat_l1_name'))

        await asyncio.sleep(random.randint(0, 5))
        await session.close()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_cat())
    loop.close()
