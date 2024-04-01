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

        print("scrapping started")

        sb = self.sb

        btns_panel: WebElement = sb.find_element('.Mdl__inv-footer .ButtonGroup__space button')

        btn_deposit = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Deposit')]")
        btn_refresh = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Refresh')]")
        btn_selectall = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Select All')]")

        items_on_site = sb.find_elements(".Inventory-item")
        print("Items total: ",len(items_on_site))

        for item_on_site in items_on_site:
            print(item_on_site.get_attribute("innerText"))
            item_text = item_on_site.get_attribute("innerText")
            name, price = scrape_text(item_text)
            print("===",name, " ",price)
            if price <= 0.0:
                continue    # unsuitable
            self.inventory.append(ItemRust(name,price_rch_bet=price))    # to nie jest price rchshop i nie powinno tak dzialac, bo tu duza cena to lepiej

        print("Items minus unsuitable: ", len(self.inventory))
    def update_inventory(self):
        """ Get current inventory for rustchance.
        Czy request do api da wystarczająco info aby selenium wiedzialo co kliknac?
        """
        # check if cookies set
        # fetch inv
        # convert to itemrust
        pass

    def select_items_taxed(self, minprice, maxprice, min_tax_frac, max_tax_frac):
        """ Select which items to bet that the bet will be taxed (in order to be able to join drop).
         minprice, maxprice - Bet amount has to be in range between those two values
         min_tax, max_tax= - Minimum and maximum fraction of total pool size (2*your_bet) that has to be
         possible to be taxed.
         There has to me an item of value between min_tax_percent*pool_size and max_tax_percent*pool_size
         """
        if not (0 <= min_tax_frac <= 1 and 0 <= max_tax_frac <= 1):
            raise ValueError("min_tax_frac and max_tax_frac has to be in range <0,1>")

        max_pool = 2*maxprice
        max_tax_general = max_tax_frac * max_pool

        selected_items = []
        add_queue = [*self.inventory]
        add_queue.sort(key=lambda item: item.price_bet/item.value_single,reverse=True)

        index,counter = 0,0
        while index < len(add_queue):
            if add_queue[index].price_bet < max_tax_general:
                add_queue.append(add_queue.pop(index))  # Move at the end of the list
            else:
                index += 1
            counter+=1
            if counter>=len(add_queue):
                break

        print("name", " ", "price", " ", "val")
        for i in add_queue:
            i: ItemRust
            print(i.name, " ", i.price_bet, " ", i.value_single)

        for item in self.inventory:
            item: ItemRust
            name = item.name
            price = item.price_bet
            value = item.value_single

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