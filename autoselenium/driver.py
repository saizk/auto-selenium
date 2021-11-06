import os
import time
import json
import shutil
from sys import platform
from pathlib import Path

from selenium.webdriver import Chrome, Firefox, Opera, Remote
from msedge.selenium_tools import Edge

from selenium.common.exceptions import SessionNotCreatedException


class Driver(object):

    _LOCAL_STORAGE = 'cookies.json'
    _BRAVE_PATHS = {
        'win32': 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe',
        'linux': '/opt/brave.com/brave/brave-browser',
        'darwin': '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
    }
    XPATH_SELECTORS = {}
    CSS_SELECTORS = {}

    def __init__(self, browser: str, root: str = '.', driver_path: str = '',
                 profile_path: str = '', brave_path: str = '',
                 headless: bool = False, kiosk: bool = False,
                 proxy: str = None, command_executor: str = None):

        self.browser = browser.lower()
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

        self._cookies_path = Path(f'{self.profile_path}/{self._LOCAL_STORAGE}')

        try:
            self.options = self._create_options()
            self.driver = self._create_selenium_driver()

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
        if self.browser == 'firefox':
            self._load_profile()
        return self.driver

    def __exit__(self, *args):
        if self.browser == 'firefox':
            self._save_profile()
        self._save_local_storage()
        return self.quit()

    def _create_selenium_driver(self):

        if self.command_executor:  # remote driver
            driver = Remote(command_executor=self.command_executor, options=self.options)

        elif self.browser in ['chrome', 'brave']:
            driver = Chrome(executable_path=self.driver_path, options=self.options)

        elif self.browser == 'opera':
            driver = Opera(executable_path=self.driver_path, options=self.options)

        elif self.browser == 'edge':
            driver = Edge(executable_path=self.driver_path, options=self.options)

        elif self.browser == 'firefox':
            from selenium.webdriver.firefox.options import FirefoxProfile

            if self.profile_path.exists():
                profile = FirefoxProfile(self.profile_path)
            else:
                profile = FirefoxProfile()

            driver = Firefox(
                executable_path=self.driver_path,
                options=self.options,
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

    def _load_profile(self):
        local_storage_file = os.path.join(self.driver.profile.path, self._cookies_path)
        if Path(local_storage_file).exists():
            with open(local_storage_file) as f:
                data = json.loads(f.read())
                self.driver.execute_script(''.join(
                    [f'window.localStorage.setItem(\'{k}\', \'{v}\'); '
                     for k, v in data.items()])
                )
            self.refresh()

    def _save_profile(self, remove_old=False):
        if self.profile_path.exists():
            return
        driver_profile, local_path = self.driver.profile.path, self.profile_path
        ignore_rule = shutil.ignore_patterns('parent.lock', 'lock', '.parentlock')
        os.mkdir(local_path)
        if remove_old:
            try:
                shutil.rmtree(local_path)
            except OSError:
                pass
            shutil.copytree(
                src=os.path.join(driver_profile), dst=local_path,
                ignore=ignore_rule,
            )
        else:
            for item in os.listdir(driver_profile):
                if item in ['parent.lock', 'lock', '.parentlock']:
                    continue
                src, dst = os.path.join(driver_profile, item), local_path
                if os.path.isdir(src):
                    shutil.copytree(src=src, dst=dst,
                                    ignore=ignore_rule)
                else:
                    shutil.copy2(src, dst)

    def _save_local_storage(self):
        with open(self._cookies_path, 'w+') as f:
            f.write(json.dumps(self.driver.execute_script('return window.localStorage;')))  # get local storage

    @staticmethod
    def retry(func, *args, **kwargs):
        time.sleep(.5)
        func(*args, **kwargs)

    def get(self, url):
        return self.driver.get(url)

    def add_css_selectors(self, selectors: dict):
        self.CSS_SELECTORS.update(selectors)

    def add_xpath_selectors(self, selectors: dict):
        self.XPATH_SELECTORS.update(selectors)

    def maximize_window(self):
        self.driver.maximize_window()

    def screenshot(self, filename):
        self.driver.save_screenshot(filename)

    def refresh(self):
        self.driver.refresh()

    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()
