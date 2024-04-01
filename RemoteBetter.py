import asyncio
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

import inspect

from ItemRust import ItemRust

# BaseCase.main(__name__, __file__)
class RemoteBetter():
    url_coinflip = "https://rustchance.com/coinflip"

    def __init__(self, sb: BaseCase):
        # self.trade_handler = SteamTradeHandler()
        self.inventory = []

        self.sb: BaseCase = sb

        if not self.sb.undetectable:
            print("!!!!!!! DRIVER IS NOT UNDETECTABLE, LEAVING !!!!!!!")
            exit()

        self.load_rch_cookies()

    def tutututu(self):
        self.sb.driver.uc_open(RemoteBetter.url_coinflip)

        #print(self.sb.find_link_text("blog"))
        #self.sb.find_link_text("blog").click()

        print("\nPresence check:")
        print(self.sb.is_element_present('.ButtonGroup__space > button[class*="Button--large"]'))

        #print(self.driver.is_element_present('.ButtonGroup__space > button[class*="Button--large"]'))

    def load_rch_cookies(self):
        sb = self.sb
        url_404 = "https://rustchance.com/coinfli"
        sb.driver.uc_open(url_404)
        sb.driver.add_cookie(
            {'domain': 'rustchance.com', 'httpOnly': False, 'name': 'pdfcc', 'path': '/', 'sameSite': 'Lax',
             'secure': True, 'value': '6'})
        sb.driver.add_cookie(
            {'domain': 'rustchance.com', 'httpOnly': False, 'name': 'fontsCssCache', 'path': '/', 'sameSite': 'Lax',
             'secure': True, 'value': 'True'})
        sb.driver.add_cookie(
            {'domain': 'rustchance.com', 'httpOnly': False, 'name': 'token', 'path': '/', 'sameSite': 'Lax',
             'secure': True, 'value': 'yHFdHulxuUwvsTvYsbtFyfaAIonwmhldcZFMUdUgEfIUBsdd'})

    def open_site_coinflip(self):
        self.sb.driver.uc_open(RemoteBetter.url_coinflip)

    def click_create_coinflip(self):
        sb = self.sb
        CREATE_COINFLIP_SELECTOR='.ButtonGroup__space .Button--large'
        CONTINUE_SELECTOR='.Modal-body__bottom  .Landmines__lobby-actions__button'

        """if not sb.is_element_present(CREATE_COINFLIP_SELECTOR):
            print(CREATE_COINFLIP_SELECTOR.__name__+" not visible")
            sb.driver.switch_to.window(sb.driver.window_handles[0])
        else:
            print("CREATE_COINFLIP visible")"""
        self.is_present_status(CREATE_COINFLIP_SELECTOR)
        sb.highlight_click(CREATE_COINFLIP_SELECTOR)

        # Confirmation window about API scams etc. click CONTINUE
        if self.is_present_status(CONTINUE_SELECTOR):
            sb.highlight_click(CONTINUE_SELECTOR)

    def scrap_eq_from_create_cf(self):
        def scrape_text(item_text):
            name, price_str = item_text.split('\n')
            if price_str.strip() == "Unsuitable":
                price = 0.0
            else:
                price = float(price_str.replace('$', ''))
            return name.strip(), price

        sb = self.sb

        # '.Mdl__inv-footer .ButtonGroup__space button'
        """btns = self.driver.find_element('.Mdl__inv-footer .ButtonGroup__space button')
        btn_select_all = btns.find_element(By.XPATH,"//*[contains(text(), 'Select all')]")
        btn_refresh = btns[1]
        btn_deposit = self.driver.find_element(By.XPATH,"//*[contains(text(), 'Deposit')]")
        btn_deposit = self.driver.find_element(By.XPATH,"//*[matches(@text,'empire burlesque','i')]")"""

        sb.driver.sleep(1)
        print("scrapping started")
        btn_refresh = None

        btns_panel:WebElement = sb.find_element('.Mdl__inv-footer .ButtonGroup__space button')

        btn_deposit = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Deposit')]")
        btn_refresh = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Refresh')]")
        btn_selectall = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Select All')]")

        items_on_site = sb.find_elements(".Inventory-item")
        items=[]
        for item_on_site in items_on_site:
            print(item_on_site.get_attribute("innerText"))
            item_text = item_on_site.get_attribute("innerText")
            name, price = scrape_text(item_text)
            print("===",name, " ",price)
            #items.append(ItemRust(name,price_rchshop=price))    # to nie jest price rchshop i nie powinno tak dzialac, bo tu duza cena to lepiej



        sb.driver.sleep(10)

    def update_inventory(self):
        """ Get current inventory for rustchance.
        Czy request do api da wystarczająco info aby selenium wiedzialo co kliknac?
        """
        # check if cookies set
        # fetch inv
        # convert to itemrust
        pass

    def select_items_taxed(self, minprice, maxprice, min_tax_percent, max_tax_percent):
        """ Select which items to bet with taxed item (in order to be able to join drop).
         minprice, maxprice - Bet amount has to be in range between those two values
         min_tax_percent, max_tax_percent - Minimum and maximum percent of total pool size (2*your_bet) that has to be possible to be taxed.
         There has to me an item of value between min_tax_percent*pool_size and max_tax_percent*pool_size
         """
        selected_items = []

        for item in self.inventory:
            name = ""  # placeholder
            price = 0  # placeholder

        return selected_items

    def bet(self, items):
        """ Bet selected items """
        pass

    def bet_if_needed(self):
        """ Bet selected items when supply period after last bet ends """
        pass

    async def wait_for_winnings_and_accept(self, time, delay):
        while True:
            # fetch
            # try to accept
            await asyncio.sleep(delay)  # wait before next fetch

    def is_present_status(self, selector):
        sb = self.sb
        var_name = [name for name, value in inspect.currentframe().f_back.f_locals.items() if value is selector][0]
        if not sb.is_element_present(selector):
            print(var_name + " not present")
            return False

        print(var_name + " present")
        return True