import asyncio

import aiohttp
import jsonpickle
from ItemRust import ItemRust
from ItemRustDatabase import ItemRustDatabase
from seleniumbase import SB

from RemoteBetter import RemoteBetter

ITEMDB_FILE = "rustItemDatabase.txt"


async def body():
    # pierwsza wersja: bierze ity za x$ z podatkiem i je betuje
    #   select prices (minprice, maxprice)
    # load cookies from rch
    # fetch inventory with prices from rch
    # select items
    # bet selected items
    # accept gifts after that

    minprice = 11.5
    maxprice = 16
    min_tax_frac = 0.02
    max_tax_frac = 0.05

    with SB(demo=True, uc=True, uc_cdp_events=True, uc_cdp=True, test=TEST_MODE) as sb:
        r = RemoteBetter(sb)

        if LOAD_INV:
            with open('inventory_data.txt', 'r') as file:
                jsonstr = file.read()
                r.inventory = jsonpickle.loads(jsonstr)
        else:
            r.load_rch_cookies()
            r.open_site_coinflip()
            r.click_create_coinflip()
            r.x()

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

        selected_items = r.select_items_taxed(minprice, maxprice, min_tax_frac, max_tax_frac)

        # r.update_inventory()
        # selected_items = r.select_items_drop(minprice, maxprice)
        # print(selected_items)
        # r.bet_if_needed()
        # await r.wait_for_winnings_and_accept()

        sb.sleep(80)


# for debugging
LOAD_INV = True
TEST_MODE = False  # do not expire db


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
