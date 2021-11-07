# -*- coding: utf-8 -*-

import time
from sys import platform
from pathlib import Path

from selenium.webdriver import Chrome, Firefox, Opera, Remote
from msedge.selenium_tools import Edge

from selenium.common.exceptions import SessionNotCreatedException


class Driver(object):

    _BRAVE_PATHS = {
        'win32': 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe',
        'linux': '/opt/brave.com/brave/brave-browser',
        'darwin': '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
    }
    XPATH_SELECTORS = {}
    CSS_SELECTORS = {}

    def __init__(self,
                 browser: str,
                 root: str = '.',
                 driver_path=None,
                 profile_path=None,
                 driver_options=None,
                 brave_path=None,
                 headless=False,
                 kiosk=False,
                 proxy=None,
                 command_executor=None):
        """
        :param (str) browser: Driver browser (i.e. 'chrome', 'firefox', 'edge', 'brave', 'opera').
        :param (str) root: Root path for the driver executable and profiles.
        :param (str) driver_path: Path for an existing driver. If empty it will search for the driver based on its name.
        :param (str) profile_path: Path for an existing profile. If empty it will create one new.
        :param (selenium.webdriver.browser.options) driver_options: Custom Selenium Options for the driver.
        :param (str) brave_path: Path for a custom installation path of Brave Browser.
        :param (bool) headless: Activate headless mode
        :param (bool) kiosk: Activate kiosk mode (does not work on Opera)
        :param (str) proxy: Set a proxy (format -> 'proxy:port')
        :param (str) command_executor: Command executor for remote Selenium driver.
        """

        self.browser = browser.lower()
        self.options = driver_options
        self.headless = headless
        self.kiosk = kiosk

        self.proxy = proxy
        self.command_executor = command_executor

        if not driver_path:
            driver_path = self._search_driver(self.browser, root)
            if not driver_path:
                driver_path = self._download_driver(self.browser, root=root)
        self.driver_path = Path(driver_path).absolute()

        if not profile_path:
            profile_path = f'{self.driver_path.parent}/{self.browser}-profile'
        self.profile_path = Path(profile_path).absolute()

        if not brave_path:
            self.brave_path = self._BRAVE_PATHS[platform]
        else:
            self.brave_path = Path(brave_path).absolute()

        try:
            if driver_options is None:
                self.options = self._create_options()

            self.driver = self._create_selenium_driver(self.options)

        except OSError as e:
            raise RuntimeError(f'Incorrect executable path for {self.browser} driver: {e}')
        except SessionNotCreatedException as e:
            raise RuntimeError(f'{e} -> Cannot create {self.browser} process with the current driver.\n'
                               f'Update your browser to the latest version or download the specific driver')

    @staticmethod
    def _download_driver(browser, root):
        from autoselenium.download import download_driver
        return download_driver(browser, root=root)

    @staticmethod
    def _search_driver(driver, root):
        from autoselenium.utils import search_driver
        return search_driver(driver, root=root)

    def __enter__(self):
        return self.driver

    def __exit__(self, *args):
        return self.quit()

    def _create_selenium_driver(self, options):

        if self.command_executor:  # remote driver
            driver = Remote(command_executor=self.command_executor, options=options)

        elif self.browser in ['chrome', 'brave']:
            driver = Chrome(executable_path=self.driver_path, options=options)

        elif self.browser == 'opera':
            driver = Opera(executable_path=self.driver_path, options=options)

        elif self.browser == 'edge':
            driver = Edge(executable_path=self.driver_path, options=options)

        elif self.browser == 'firefox':
            from selenium.webdriver.firefox.options import FirefoxProfile

            if self.profile_path.exists():
                profile = FirefoxProfile(self.profile_path)
            else:
                profile = FirefoxProfile()

            driver = Firefox(
                executable_path=self.driver_path,
                options=options,
                firefox_profile=profile,
                service_log_path=Path(f'{self.driver_path.parent}/geckodriver.log')
            )
        else:
            raise RuntimeError(f'Cannot load Selenium driver for {self.browser}')

        return driver

    def _create_options(self):

        if self.browser in ['chrome', 'brave']:
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            options = ChromeOptions()
            if self.browser == 'brave':
                options.binary_location = self.brave_path

        elif self.browser == 'firefox':
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            options = FirefoxOptions()
            options.set_preference('dom.webnotifications.enabled', False)

        elif self.browser == 'opera':
            from selenium.webdriver.opera.options import Options as OperaOptions
            options = OperaOptions()

        elif self.browser == 'edge':
            from msedge.selenium_tools import EdgeOptions
            options = EdgeOptions()
            options.use_chromium = True
        else:
            raise RuntimeError(f'Unknown browser {self.browser}')

        options.headless = self.headless
        if self.kiosk:  # not supported on opera driver
            if self.browser == 'opera': print('Opera does not work on kiosk mode')
            options.add_argument('--kiosk')

        if self.browser != 'firefox':
            options.add_argument(f'user-data-dir={self.profile_path}')
            options.add_argument('--disable-notifications')

        if self.proxy is not None:
            options = self._set_proxy(options)

        return options

    def _set_proxy(self, options):
        if self.browser != 'firefox':
            options.add_argument(f'--proxy-server={self.proxy}')
            return options
        return self._set_firefox_proxy(options)

    def _set_firefox_proxy(self, options):
        proxy_address, proxy_port = self.proxy.split(':')
        options.set_preference('network.proxy.type', 1)
        options.set_preference('network.proxy.http', proxy_address)
        options.set_preference('network.proxy.http_port', int(proxy_port))
        options.set_preference('network.proxy.ssl', proxy_address)
        options.set_preference('network.proxy.ssl_port', int(proxy_port))
        return options

    @staticmethod
    def retry(func, *args, **kwargs):
        time.sleep(.5)
        func(*args, **kwargs)

    def get(self, url):
        return self.driver.get(url)

    def refresh(self):
        self.driver.refresh()

    def quit(self):
        self.driver.quit()
