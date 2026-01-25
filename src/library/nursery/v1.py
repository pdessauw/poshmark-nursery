"""Version 1.0 of the PoshNursery, able to share an entire closter"""

import pickle
import random
import sys
import time
from pathlib import Path

import undetected as uc
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait

from library.logging import LOGGER


class PoshNursery:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.loginID = "login_form_username_email"
        self.loginXPath = "//input[@name='userHandle']"
        self.passwordID = "login_form_password"
        self.passwordXPath = "//input[@name='password']"

        self.cookies_fpath = Path("./cookies.bin")
        self.driver = uc.Chrome()
        self.width = 1250
        self.height = 750
        self.driver.set_window_size(self.width, self.height)
        self.wait_range = [0.3, 0.5]

        self.vars = {}

    def dump_cookies(self):
        with open("cookies.bin", "wb") as fp:
            pickle.dump(self.driver.get_cookies(), fp)  # noqa

    def load_cookies(self):
        self.driver.delete_all_cookies()

        with open("cookies.bin", "rb") as fp:
            cookie_list = pickle.load(fp)

        for cookie in cookie_list:
            self.driver.add_cookie(cookie)

    def teardown(self):
        self.dump_cookies()
        self.driver.quit()

    def wait_till_clickable(self, find_by_id_or_path, id_or_path, time_out_secs=10):
        locator_type = By.ID if find_by_id_or_path == "id" else By.XPATH

        try:
            clickable_element = WebDriverWait(self.driver, time_out_secs).until(
                EC.element_to_be_clickable((locator_type, id_or_path))
            )
        except TimeoutException as e:
            LOGGER.error(
                "Timed out at locating element by %s at %s: %s",
                find_by_id_or_path,
                str(id_or_path),
                str(e),
            )
            return False

        return clickable_element

    def get_login_element(self, element_id, element_xpath):
        element = self.wait_till_clickable("id", element_id)
        if not element:
            LOGGER.warning("Time out at locating ID: " + element_id)
            element = self.wait_till_clickable("xpath", element_xpath)
            if not element:
                LOGGER.error("Timed out again with xpath")
                LOGGER.error(
                    "Please manually enter username/password, then type 'c' or 'continue'"
                )
        return element

    def enter_text_slowly(self, element, text):
        for char in text:
            element.send_keys(char)
            self.wait(0.5)

    def enter_username(self):
        username_element = self.get_login_element(self.loginID, self.loginXPath)
        if not username_element:
            LOGGER.error("Username element not obtained from page, exiting...")
            self.teardown()
            sys.exit()
        self.enter_text_slowly(username_element, self.username)

    def enter_and_submit_password(self):
        password_element = self.get_login_element(self.passwordID, self.passwordXPath)
        if not password_element:
            LOGGER.error("Password element not obtained from page, exiting...")
            self.teardown()
            sys.exit()
        self.enter_text_slowly(password_element, self.password)
        password_element.submit()

    def get_clickable_element(
        self, selector_type, selector_locator, root_element=None, retries=5
    ):
        last_exc = None
        wait_multiplier = 2

        if not root_element:
            root_element = self.driver

        for _ in range(retries):
            try:
                return root_element.find_element(selector_type, selector_locator)
            except NoSuchElementException as e:
                last_exc = e
                self.wait(wait_multiplier)

            wait_multiplier *= 2  # If an error is detected, raise the wait threshold.

        # After retries are exhausted, re-raise or handle
        raise last_exc

    def navigate_and_click(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.wait()

        element.click()
        self.wait()

    def wait(self, multiplier: float = 1.0):
        time.sleep(
            random.uniform(
                self.wait_range[0] * multiplier, self.wait_range[1] * multiplier
            )
        )

    def login(self):
        login_element = self.get_clickable_element(By.LINK_TEXT, "Log in")
        self.navigate_and_click(login_element)

        try:
            WebDriverWait(self.driver, 10).until(EC.title_contains("Log In"))
        except Exception as e:
            LOGGER.error(f"ERROR: Cannot find 'Log In' element in page: {str(e)}")
            self.teardown()
            sys.exit()

        self.enter_username()
        self.wait()
        self.enter_and_submit_password()

        try:
            WebDriverWait(self.driver, 60).until(EC.title_contains("Feed"))
        except Exception as e:
            LOGGER.error(f"ERROR: {str(e)}")
            self.teardown()
            sys.exit()

    def wait_for_offset(
        self,
        wait_multiplier: float = 1,
        do_scroll: int = 0,
        expected_offset: int = -1,
        max_tries: int = 10,
    ):
        LOGGER.debug(
            "(wait_for_offset) wait_multiplier: %f; do_scroll: %d; expected_offset: %d; max_tries: %d",
            wait_multiplier,
            do_scroll,
            expected_offset,
            max_tries,
        )
        tries = 0
        reached_expected_offset = False
        last_offset = (
            self.driver.execute_script("return pageYOffset")
            if expected_offset == -1
            else expected_offset
        )

        while tries < max_tries and not reached_expected_offset:
            self.driver.execute_script(f"window.scrollBy(0, {do_scroll * self.height});")
            self.wait(wait_multiplier)

            current_offset = self.driver.execute_script("return pageYOffset")
            reached_expected_offset = last_offset == current_offset

            LOGGER.debug(
                "Page offset: Current %s; Last: %s", current_offset, last_offset
            )
            if expected_offset == -1:
                last_offset = current_offset

            tries += 1

        if tries == max_tries and not reached_expected_offset:
            message = "Offset not reached in the number of allowed tries."
            raise Exception(message)

    def share_closet(self):
        self.driver.get("https://poshmark.com/")
        self.wait()

        if self.cookies_fpath.exists():
            self.load_cookies()

        self.driver.get("https://poshmark.com/")
        self.wait()

        if "Feed" not in self.driver.title:  # User is not yet logged in
            self.login()

        # Open user profile dropdown
        user_dropdown_selector = ".user-image.user-image--s"
        user_dropdown_element = self.get_clickable_element(
            By.CSS_SELECTOR, user_dropdown_selector
        )
        self.navigate_and_click(user_dropdown_element)

        # Click on My Closet
        user_closet_selector = "li.dropdown__menu__item:nth-child(1)"
        user_closet_element = self.get_clickable_element(
            By.CSS_SELECTOR, user_closet_selector
        )
        self.navigate_and_click(user_closet_element)

        # Open Bulk Tools dropdown
        bulk_tools_selector = ".icon.icon-bulk-tools"
        bulk_tools_element = self.get_clickable_element(
            By.CSS_SELECTOR, bulk_tools_selector
        )
        self.navigate_and_click(bulk_tools_element)

        # Click on Share to Followers options
        share_to_followers_dropdown = (
            "div.dropdown__link[data-et-name='share_to_followers']"
        )
        share_to_followers_element = self.get_clickable_element(
            By.CSS_SELECTOR, share_to_followers_dropdown
        )
        self.navigate_and_click(share_to_followers_element)

        # Filter by closet
        closet_input_element = self.get_clickable_element(
            By.CSS_SELECTOR, "input[value='closet']"
        )
        closet_div_element = self.get_clickable_element(
            By.XPATH, "..", root_element=closet_input_element
        )
        self.navigate_and_click(closet_div_element)

        # Filter by women
        women_element = self.get_clickable_element(
            By.CSS_SELECTOR, "a[data-et-prop-content='Women']"
        )
        self.navigate_and_click(women_element)

        # Scroll twice so that the "Availability" section is on screen
        for _ in range(2):
            self.driver.execute_script(f"window.scrollBy(0, {self.height});")
            self.wait()

        # Filter by available
        closet_input_element = self.get_clickable_element(
            By.CSS_SELECTOR, "input[name='availability'][value='available']"
        )
        closet_div_element = self.get_clickable_element(
            By.XPATH, "..", root_element=closet_input_element
        )
        self.navigate_and_click(closet_div_element)

        # Scroll down to display all items and wait between 1.5 and 2.5 seconds to ensure
        # it is impossible to scroll further
        self.wait_for_offset(
            wait_multiplier=5, do_scroll=1, expected_offset=-1, max_tries=1_000
        )

        # Scroll back to top
        scroll_to_top_button = self.get_clickable_element(
            By.CSS_SELECTOR, "button[data-et-name='scroll_to_top']"
        )
        self.navigate_and_click(scroll_to_top_button)

        # We wait between 0.6 and 1 seconds to check if we are at offset 0. Throw an
        # error after 10 tries.
        self.wait_for_offset(
            wait_multiplier=2, do_scroll=0, expected_offset=0, max_tries=10
        )

        # Select all
        select_all_text_element = self.get_clickable_element(
            By.CSS_SELECTOR, "section.main__column > div.d--fl > div.tile__checkbox"
        )
        self.navigate_and_click(select_all_text_element)

        # Share to followers
        share_to_followers_button = self.get_clickable_element(
            By.CSS_SELECTOR, "button.btn[data-et-name='share_to_followers']"
        )
        self.navigate_and_click(share_to_followers_button)

        # Wait that the offset has not moved in the last X secondes
        wait_multiplier = 10.0
        for _ in range(5):
            try:
                self.wait_for_offset(
                    wait_multiplier=7, do_scroll=0, expected_offset=-1, max_tries=1_000
                )
            except Exception as exc:
                LOGGER.warning(
                    "An unexpected exception occurred while waiting for sharing to "
                    "finish: %s",
                    str(exc),
                )
                self.wait(wait_multiplier)
                wait_multiplier *= 1.5

        self.teardown()
        sys.exit()
