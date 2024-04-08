import asyncio

import aiohttp
import jsonpickle
from ItemRust import ItemRust
from ItemRustDatabase import ItemRustDatabase
from seleniumbase import SB

from RemoteBetter import RemoteBetter

ITEMDB_FILE = "rustItemDatabase.txt"
# for debugging
LOAD_INV = 0
TEST_MODE = True  # do not expire db and other

async def body():
    # pierwsza wersja: bierze ity za x$ z podatkiem i je betuje
    #   select prices (minprice, maxprice)
    # load cookies from rch
    # fetch inventory with prices from rch
    # select items
    # bet selected items
    # accept gifts after that

    minprice = 11.5 - 4
    maxprice = 16 - 4
    min_tax_frac = 0.02
    max_tax_frac = 0.1

    async def get_inventory():
        if LOAD_INV:
            with open('inventory_data.txt', 'r') as file:
                jsonstr = file.read()
                r.inventory = jsonpickle.loads(jsonstr)
        else:
            r.load_rch_cookies()
            r.open_site_coinflip()
            r.click_create_coinflip()
            r.scrap_eq_from_create_cf()

            with open('inventory_data.txt', 'w') as file:
                jsonstr = jsonpickle.dumps(r.inventory)
                file.write(jsonstr)

        tasks = []
        for item in r.inventory:
            item: ItemRust
            task = asyncio.create_task(item.update_async())
            tasks.append(task)
        for task in tasks:
            try:
                await task
            except aiohttp.client_exceptions.ClientConnectorError as e:
                print("Connection error: " + str(e))

        r.inventory = list(filter(lambda x: x.all_success, r.inventory))
        print("Items minus failures: ", len(r.inventory))

    with SB(demo=False, uc=True, uc_cdp_events=True, uc_cdp=True, test=TEST_MODE) as sb:
        r = RemoteBetter(sb)

        await get_inventory()

        selected_items = r.select_items_taxed(minprice, maxprice, min_tax_frac, max_tax_frac)

        # Select items in UI
        r.deposit_cf_items_UI(selected_items)



        sb.sleep(80)


async def main():
    itemdb = ItemRustDatabase(ITEMDB_FILE, do_not_expire=TEST_MODE)
    itemdb.load_database()
    ItemRust.set_database(itemdb)

    async with aiohttp.ClientSession() as session:
        ItemRust.set_session(session)
        try:
            await body()
        finally:
            itemdb.save_database()


if __name__ == "__main__":
    asyncio.run(main())
