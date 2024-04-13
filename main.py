import asyncio
import configparser
import os
import sys
import time
from datetime import datetime, timedelta

import aiohttp
import jsonpickle
from ItemRust import ItemRust
from ItemRustDatabase import ItemRustDatabase
from SteamTradeHandler import SteamTradeHandler
from fernet_wrapper import Wrapper
from seleniumbase import SB
from selenium.webdriver.remote.webelement import WebElement

from RemoteBetter import RemoteBetter


async def update_rustitems(remote_better):
    tasks = []

    # stworz liste unikalnych itow
    # update ich
    # sklonuj je odpowiednia ilosc razy?
    # czy lepiej quantity na nich ustawic

    start_time = time.time()

    for item in remote_better.inventory:
        item: ItemRust
        task = asyncio.create_task(item.update_async())
        tasks.append(task)

    for task in tasks:
        try:
            await task
        except aiohttp.client_exceptions.ClientConnectorError as e:
            print("Connection error: " + str(e))

    end_time = time.time()
    execution_time = end_time - start_time
    print("Czas wykonania:", execution_time, "sekund")

    remote_better.inventory = list(filter(lambda x: x.all_success, remote_better.inventory))
    print("Items minus failures: ", len(remote_better.inventory))

async def test(remote_better):
    ".pt-intent-danger"
    r = remote_better
    r.load_rch_cookies(TOKEN_FILEPATH)
    r.sb.driver.uc_open("https://rustchance.com/easter-event")
    btns = r.sb.find_elements(".event-button.event-case__open")
    print(r.sb.is_element_present(".pt-intent-danger"))
    #print(".event-button.event-case__open")
    1==1

    print(r.sb.is_element_present(".supplydrops-button"))
    spl=r.sb.find_element(".supplydrops-button")
    spl.click()
    await asyncio.sleep(6)
    print(r.sb.is_element_in_an_iframe(".ctp-checkbox-label"))
    r.sb.switch_to_frame(0)  # Przełącz na pierwszy iframe na stronie
    r.sb.click(".ctp-checkbox-label")  # Kliknij przycisk z klasą .ctp-checkbox-label

    print(r.sb.is_element_present(".pt-intent-danger"))


    await asyncio.sleep(20)
    btns[0].click()
    await asyncio.sleep(1)
    btns[0].click()
    await asyncio.sleep(1)
    btns[0].click()

    print(r.sb.is_element_present(".pt-intent-danger"))
    #await asyncio.sleep(8)

    warns = r.sb.find_elements(".pt-intent-danger")
    warn = warns[0]

    for warn in warns:
        warn:WebElement
        print(warn.text)

    print("slep")
    await asyncio.sleep(10)



    return

async def get_inventory(remote_better):
    if LOAD_INV:
        with open('inventory_data.txt', 'r') as file:
            jsonstr = file.read()
            remote_better.inventory = jsonpickle.loads(jsonstr)
            if LOAD_5_ITEMS:  # for debugging
                remote_better.inventory = remote_better.inventory[:5]
            else:
                remote_better.inventory = remote_better.inventory

    else:
        remote_better.load_rch_cookies(TOKEN_FILEPATH)
        remote_better.open_site_coinflip()
        remote_better.click_create_coinflip()
        remote_better.scrap_eq_from_create_cf()

        with open('inventory_data.txt', 'w') as file:
            jsonstr = jsonpickle.dumps(remote_better.inventory)
            file.write(jsonstr)

    await update_rustitems(remote_better)


async def accept_offers(key, gifts_only, max_wait_time=None, delay=None):
    print("Accept offers...")
    th = SteamTradeHandler.create_account_from_encrypted_file(key, ACC_FILE, TRADE_WHITELIST)
    print(th.accept_all_offers(gifts_only=gifts_only))


def time_after(sec):
    target_time = datetime.now() + timedelta(seconds=sec)
    return target_time.strftime("%H:%M")


async def body():
    min_tax_frac = 0.02
    max_tax_frac = 0.05

    while True:
        with SB(demo=False, uc=True, uc_cdp_events=True, uc_cdp=True, test=TEST_MODE, headless=HEADLESS) as sb:
            r = RemoteBetter(sb)

            if TEST_MODE:
                await test(r)
                print("sleeping 40ss")
                await asyncio.sleep(40)

            # Scrape inventory from site
            await get_inventory(r)

            # Which items to select
            selected_items = r.select_items_taxed(minprice, maxprice, min_tax_frac, max_tax_frac)

            # Select items in UI (click them)
            await r.deposit_cf_items_UI(selected_items)

            _ = asyncio.create_task(ItemRust.database.save_database_async())  # Not awaited because there's no need to

            print("Time: ", datetime.now().strftime("%d-%m %H:%M"))

            # Accept trade (to site)
            try:
                await asyncio.sleep(5)
                await accept_offers(global_key, gifts_only=False)
            except Exception as e:
                print("Trade accept error: " + str(e))
            print("Waiting 60sec...")

            await asyncio.sleep(60)
            print("Next bet at ~", time_after(11830))

            try:
                await accept_offers(global_key, gifts_only=False)
            except Exception as e:
                print("Trade accept error: " + str(e))
            print("Waiting 110sec...")

            await asyncio.sleep(110)

            try:
                await accept_offers(global_key, gifts_only=True)
            except Exception as e:
                print("Trade accept error: " + str(e))
            print("Waiting 710sec... (and then even longer)")

            # Accept trade (from site, possible winning)
            await asyncio.sleep(710)
            _ = asyncio.create_task(ItemRust.database.save_database_async())  # Not awaited because there's no need to
            for i in range(11):
                await asyncio.sleep(1000)
                print(f"Sleep {(i + 1) * 1000}/11000 sec passed")
        print("Wyszlo z petli, super")


def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)

    global ITEMDB_FILE, LOAD_PASS, LOAD_INV, LOAD_5_ITEMS, TEST_MODE, HEADLESS
    global TRADE_WHITELIST, MODE
    global DATA_DICT

    ITEMDB_FILE = config.get('Global', 'ITEMDB_FILE')
    LOAD_PASS = config.getboolean('Global', 'LOAD_PASS')
    LOAD_INV = config.getboolean('Global', 'LOAD_INV')
    LOAD_5_ITEMS = config.getboolean('Global', 'LOAD_5_ITEMS')
    TEST_MODE = config.getboolean('Global', 'TEST_MODE')
    HEADLESS = config.getboolean('Global', 'HEADLESS')

    TRADE_WHITELIST = [int(id.strip()) for id in config.get('Global', 'TRADE_WHITELIST').split(',')]

    MODE = config.get('Global', 'MODE')

    DATA_DICT = {
        'wotanex': {
            'TOKEN_FILEPATH': config.get('Global', 'TOKEN_FILEPATH_wotanex',fallback=None),
            'ACC_FILE': config.get('Global', 'ACC_FILE_wotanex',fallback=None),
            'minprice': config.getfloat('Global', 'minprice_wotanex',fallback=None),
            'maxprice': config.getfloat('Global', 'maxprice_wotanex',fallback=None)
        },
        'dark': {
            'TOKEN_FILEPATH': config.get('Global', 'TOKEN_FILEPATH_dark',fallback=None),
            'ACC_FILE': config.get('Global', 'ACC_FILE_dark',fallback=None),
            'minprice': config.getfloat('Global', 'minprice_dark',fallback=None),
            'maxprice': config.getfloat('Global', 'maxprice_dark',fallback=None)
        }
    }


def _pre_start_operations():
    read_config('config.txt')

    global TOKEN_FILEPATH, ACC_FILE, minprice, maxprice, global_key
    try:
        data = DATA_DICT[MODE]
        TOKEN_FILEPATH = data["TOKEN_FILEPATH"]
        ACC_FILE = data["ACC_FILE"]
        minprice = data["minprice"]
        maxprice = data["maxprice"]
    except Exception as e:
        print("Error while assigning data (probably wrong mode name)\n" + str(e))
        sys.exit()

    print("Mode = ", MODE)
    if "dark" not in DATA_DICT.keys():
        raise RuntimeError("dark not in DATA_DICT, possible miss while trying to warn to use vpn")
    if MODE == "dark":
        print("================ USE VPN ===================")
        print("================ USE VPN ===================")
        print("================ USE VPN ===================")
        print("================ USE VPN ===================")
        print("================ USE VPN ===================")
        input("Press key to continue")
        input("Press key to continue")
    if MODE == "wotanex":
        print("##### DISABLE vpn !!! #####")
        print("##### DISABLE vpn !!! #####")
        print("##### DISABLE vpn !!! #####")
        print("##### DISABLE vpn !!! #####")
        input("Press key to continue")
        input("Press key to continue")

    if not LOAD_PASS:  # for debugging
        global_key = Wrapper.key_from_pass(password=input("Provide password: "))
        os.system('cls')
    else:
        with open("testpass.txt", 'r') as file:
            global_key = Wrapper.key_from_pass(file.read())
            print("PASS FROM FILE USED")

async def main():
    # Loading data:
    arguments = sys.argv[:]
    print("Arguments:", arguments)

    _pre_start_operations()

    itemdb = ItemRustDatabase(ITEMDB_FILE, do_not_expire=TEST_MODE)
    itemdb.load_database()
    ItemRust.set_database(itemdb)
    ItemRustDatabase._verbose_level = 1

    if len(arguments) > 1:
        wait_time = int(arguments[1])
        print(f"Waiting {wait_time}s before start. Start at ~",time_after(wait_time))

        await asyncio.sleep(wait_time)

    async with aiohttp.ClientSession() as session:
        ItemRust.set_session(session)
        try:
            await body()
        finally:
            itemdb.save_database()


if __name__ == "__main__":
    asyncio.run(main())
