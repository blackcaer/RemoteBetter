import asyncio

from RemoteBetter import RemoteBetter
from seleniumbase import SB

from SteamTradeHandler import SteamTradeHandler
from ItemRust import ItemRust

async def main():

    # pierwsza wersja: bierze ity za x$ z podatkiem i je betuje
    #   select prices (minprice, maxprice)
    # load cookies from rch
    # fetch inventory with prices from rch
    # select items
    # bet selected items
    # accept gifts after that


    with SB(demo=True,uc=True, uc_cdp_events=True, uc_cdp=True,test=False) as sb:
        r = RemoteBetter(sb)

        minprice,maxprice=11,18

        #while 1:
        r.open_site_coinflip()
        #r.tutututu()
        r.click_create_coinflip()
        r.scrap_eq_from_create_cf()

            #r.update_inventory()
            #selected_items = r.select_items_drop(minprice, maxprice)
            #print(selected_items)
            #r.bet_if_needed()
            #await r.wait_for_winnings_and_accept()

        sb.sleep(80)


if __name__ == "__main__":
    asyncio.run(main())
