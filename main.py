import asyncio

import aiohttp
from ItemRustDatabase import ItemRustDatabase

from RemoteBetter import RemoteBetter
from seleniumbase import SB
import jsonpickle

from SteamTradeHandler import SteamTradeHandler
from ItemRust import ItemRust

ITEMDB_FILE = "rustItemDatabase.txt"


async def body():
    # pierwsza wersja: bierze ity za x$ z podatkiem i je betuje
    #   select prices (minprice, maxprice)
    # load cookies from rch
    # fetch inventory with prices from rch
    # select items
    # bet selected items
    # accept gifts after that

    LOAD_INV=True  # for debugging
    minprice, maxprice = 11, 15

    with SB(demo=True,uc=True, uc_cdp_events=True, uc_cdp=True,test=False) as sb:
        r = RemoteBetter(sb)

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

        tasks=[]
        for item in r.inventory:
            item:ItemRust
            task = asyncio.create_task(item.update_async())
            tasks.append(task)
        for task in tasks:
            await task

        r.inventory = list(filter(lambda x:x.all_success,r.inventory))
        print("Items minus failures: ",len(r.inventory))

        selected_items = r.select_items_taxed(minprice,maxprice,0.02,0.05)

        if LOAD_INV:
            return

        #r.update_inventory()
        #selected_items = r.select_items_drop(minprice, maxprice)
        #print(selected_items)
        #r.bet_if_needed()
        #await r.wait_for_winnings_and_accept()

        sb.sleep(80)


async def main():
    itemdb = ItemRustDatabase(ITEMDB_FILE)
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

