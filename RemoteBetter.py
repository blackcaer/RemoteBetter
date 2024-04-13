import asyncio
import inspect

from ItemRust import ItemRust
from prettytable import PrettyTable
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import BaseCase


class RemoteBetter():
    url_coinflip = "https://rustchance.com/coinflip"

    def __init__(self, sb: BaseCase):
        # self.trade_handler = SteamTradeHandler()
        self.inventory = []

        self.sb: BaseCase = sb

        if not self.sb.undetectable:
            print("!!!!!!! DRIVER IS NOT UNDETECTABLE, LEAVING !!!!!!!")
            exit()

    def load_rch_cookies(self, token_filepath):
        sb: BaseCase = self.sb

        # Load token from file
        with open(token_filepath, 'r') as file:
            print("Reading token from file")
            token = file.read()
            if not token:
                raise ValueError("Token file cannot be empty")

        url_404 = "https://rustchance.com/coinfli"
        sb.driver.uc_open(url_404)

        sb.driver.add_cookie(
            {'domain': 'rustchance.com', 'httpOnly': False, 'name': 'fontsCssCache', 'path': '/', 'sameSite': 'Lax',
             'secure': True, 'value': 'True'})
        sb.driver.add_cookie(
            {'domain': 'rustchance.com', 'httpOnly': False, 'name': 'token', 'path': '/', 'sameSite': 'Lax',
             'secure': True, 'value': token})

    def open_site_coinflip(self):
        self.sb.driver.uc_open(RemoteBetter.url_coinflip)

    def click_create_coinflip(self):
        sb: BaseCase = self.sb
        CREATE_COINFLIP_SELECTOR = '.ButtonGroup__space .Button--large'
        CONTINUE_SELECTOR = '.Modal-body__bottom  .Landmines__lobby-actions__button'

        """if not sb.is_element_present(CREATE_COINFLIP_SELECTOR):
            print(CREATE_COINFLIP_SELECTOR.__name__+" not visible")
            sb.driver.switch_to.window(sb.driver.window_handles[0])
        else:
            print("CREATE_COINFLIP visible")"""
        sb.wait_for_selector(CREATE_COINFLIP_SELECTOR)
        # self.is_present_status(CREATE_COINFLIP_SELECTOR)
        sb.click(CREATE_COINFLIP_SELECTOR)

        # Site shows confirmation window about API scams etc. click CONTINUE
        if self.is_present_status(CONTINUE_SELECTOR):
            sb.click(CONTINUE_SELECTOR)

    @staticmethod
    def _scrape_text_create_cf_items(item):
        """ Gets .Inventory-item and scrapes text from it.
        Returns (name,price)
        """
        item_text = item.get_attribute("innerText")
        name, price_str = item_text.split('\n')
        if price_str.strip() == "Unsuitable":
            price = 0.0
        else:
            price = float(price_str.replace('$', ''))
        return name.strip(), price

    def scrap_eq_from_create_cf(self):

        sb: BaseCase = self.sb
        wait = WebDriverWait(sb.driver, 20)

        btns_panel: WebElement = sb.find_element('.Mdl__inv-footer .ButtonGroup__space button')
        # btn_deposit = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Deposit')]")
        # btn_refresh = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Refresh')]")
        # btn_selectall = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Select All')]")

        _ = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "Inventory-items__inner")))
        print("Refreshing inventory")
        sb.click("//*[contains(text(), 'Refresh')]", by=By.XPATH)

        _ = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "Inventory-items__inner")))

        print("scrapping started")

        items_on_site = sb.find_elements(".Inventory-item")
        print("Items total: ", len(items_on_site))

        for item_on_site in items_on_site:
            name, price = self._scrape_text_create_cf_items(item_on_site)
            if price <= 0.0:
                continue  # unsuitable
            self.inventory.append(ItemRust(name,
                                           price_rch_bet=price))

        print("Items minus unsuitable: ", len(self.inventory))

    async def deposit_cf_items_UI(self, selected_items):
        sb: BaseCase = self.sb
        names_to_select = [item.name for item in selected_items]

        btns_panel: WebElement = sb.find_element('.Mdl__inv-footer .ButtonGroup__space button')
        btn_deposit = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Deposit')]")
        # btn_refresh = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Refresh')]")
        # btn_selectall = btns_panel.find_element(By.XPATH, "//*[contains(text(), 'Select All')]")

        wait = WebDriverWait(sb.driver, 10)
        _ = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "Inventory-items__inner")))

        items_on_site = sb.find_elements(".Inventory-item")

        for item in items_on_site:
            item_name, price = self._scrape_text_create_cf_items(item)
            for idx, nts in enumerate(names_to_select):
                if item_name == nts:
                    ActionChains(sb.driver).move_to_element(item).click().perform()
                    names_to_select.pop(idx)
                    await asyncio.sleep(0.2)
                    break

        print("Clicking depo in 2sec")
        await asyncio.sleep(2)
        btn_deposit.click()

    def select_items_taxed(self, min_bet, max_bet, min_tax_frac, max_tax_frac, max_item_count=10):
        """ Select which items to bet that the bet will be taxed (in order to be able to join drop).
         minprice, maxprice - Bet amount has to be in range between those two values
         min_tax, max_tax= - Minimum and maximum fraction of total pool size (2*your_bet) that has to be
         possible to be taxed.
         There has to me an item of value between min_tax_percent*pool_size and max_tax_percent*pool_size
         """
        compare_func_for_queue = lambda item: item.price_bet / item.value_single

        def _print_items(itemrust_tab):
            tab = PrettyTable(["name", "price", "val", "price/val"])

            if not itemrust_tab:
                print("itemrus_tab: ", itemrust_tab)
                print(tab)
                print("Total price: 0$")
                return

            total_price = 0
            for i in itemrust_tab:
                i: ItemRust
                tab.add_row([i.name, i.price_bet, i.value_single,
                             round(compare_func_for_queue(i), 2)
                             ])
                total_price += i.price_bet

            print(tab)
            print(f"Total price: {round(total_price, 2)}$")

        def create_queue(inventory):
            add_queue = [*inventory]
            add_queue.sort(key=compare_func_for_queue, reverse=True)
            taxables = []
            index, counter = 0, 0
            while index < len(add_queue):
                if add_queue[index].price_bet < max_tax_general:
                    taxable = add_queue.pop(index)
                    add_queue.append(taxable)  # Move at the end of the list
                    taxables.append(taxable)
                else:
                    index += 1
                counter += 1
                if counter >= len(add_queue):
                    break

            return add_queue, taxables

        def _find_good_items(queue, minp, maxp, starting_sum=0.0):

            queue = [*queue]
            items = []
            curr_sum = starting_sum

            for qi in queue:
                qi: ItemRust
                new_sum = curr_sum + qi.price_bet

                if hasattr(qi, 'selected') and qi.selected:  # So it doesn't take taxed items two times
                    continue
                if new_sum > maxp:
                    continue
                elif new_sum > minp:
                    # new sum in <minp,maxp>
                    items.append(qi)
                    return items
                else:  # new_sum < minp
                    items.append(qi)
                    curr_sum = new_sum

            return None

        def select(add_queue, taxables):
            tax_asc = sorted(taxables, key=lambda x: x.price_bet)
            # TODO przygotowac na edge case'y, na razie podstawowa funkcjonalnosc
            result = None

            for tax in tax_asc:
                tax: ItemRust
                minp = max(round(tax.price_bet / (2 * max_tax_frac), 2), min_bet)
                maxp = min(round(tax.price_bet / (2 * min_tax_frac), 2), max_bet)
                if minp >= maxp:
                    continue

                tax.selected = True
                items_in_range = _find_good_items(add_queue, minp, maxp, starting_sum=tax.price_bet)
                if items_in_range:
                    del tax.selected
                    result = [tax] + items_in_range
                    break
                tax.selected = False

            return result

        if not (0 <= min_tax_frac <= 1 and 0 <= max_tax_frac <= 1):
            raise ValueError("min_tax_frac and max_tax_frac has to be in range <0,1>")

        max_pool = 2 * max_bet  # Your and your opponent's bet
        max_tax_general = max_tax_frac * max_pool  # Max possible tax

        add_queue, taxables = create_queue(self.inventory)  # add_queue - all items, taxables - items

        print("\nAdd queue:")
        _print_items(add_queue)
        print("\nTaxables:")
        _print_items(taxables)

        selected_items = select(add_queue, taxables)

        print("\n\n Selected items:")
        _print_items(selected_items)

        return selected_items

    async def wait_for_winnings_and_accept(self, time, delay):
        while True:
            # fetch
            # try to accept
            await asyncio.sleep(delay)  # wait before next fetch

    def is_present_status(self, selector, by=By.CSS_SELECTOR):
        sb: BaseCase = self.sb
        # Searching for variable name
        try:
            var_name = [name for name, value in inspect.currentframe().f_back.f_locals.items() if value is selector][0]
        except Exception as e:
            var_name = "unknown"
        # Checking presence
        if not sb.is_element_present(selector, by=by):
            print(var_name + " not present")
            return False

        print(var_name + " present")
        return True
