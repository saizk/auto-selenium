# -*- coding: utf-8 -*-

from sys import platform
from pathlib import Path

import autoselenium.browsers as brw


DRIVER_URLS = {
    'chrome': 'https://chromedriver.storage.googleapis.com',
    'firefox': 'https://github.com/mozilla/geckodriver/releases/download',
    'opera': 'https://github.com/operasoftware/operachromiumdriver/releases/download',
    'edge': 'https://msedgedriver.azureedge.net',
    'brave': 'https://chromedriver.storage.googleapis.com',
}


def get_driver_name(driver):
    if driver == 'firefox':
        return 'gecko'
    elif driver == 'brave':
        return 'chrome'
    elif driver == 'edge':
        return 'msedge'
    return driver


def gen_driver_url(driver, version, os, bits, format_):
    root = DRIVER_URLS[driver]
    if driver == 'chrome' or driver == 'brave':
        return f'{root}/{version}/chromedriver_{os}{bits}.{format_}'
    elif driver == 'firefox':
        return f'{root}/{version}/geckodriver-{version}-{os}{bits}.{format_}'
    elif driver == 'opera':
        return f'{root}/{version}/operadriver_{os}{bits}.{format_}'
    elif driver == 'edge':
        return f'{root}/{version}/edgedriver_{os}{bits}.{format_}'


def gen_url(driver, version):
    bits = 64
    if platform == 'win32' and driver in ['chrome', 'brave']:
        bits = 32
    elif platform == 'darwin' and driver == 'firefox':
        bits = 'os'

    file_ext = 'zip'
    if platform in ['linux', 'darwin'] and driver == 'firefox':
        file_ext = 'tar.gz'

    url = gen_driver_url(driver, version, get_os(), bits, file_ext)
    filename = url.split('/')[-1]
    return url, filename


def get_latest_version(browser):
    if browser in ['chrome', 'brave']:
        version = brw.get_chromium_latest_release(browser)
    elif browser in ['firefox', 'opera']:
        version = brw.get_github_latest_release(browser)
    elif browser == 'edge':
        version = brw.get_edge_latest_release()
    else:
        raise RuntimeError(f'Cannot get latest release for {browser} browser')
    return version


def get_current_version(browser):
    if browser in ['chrome', 'brave']:
        version = brw.get_chromium_latest_release(driver=browser, current_version=True)
    elif browser in ['firefox', 'opera']:
        version = brw.get_github_latest_release(browser)
    elif browser == 'edge':
        version = brw.get_browser_version_windows(browser)
    else:
        raise RuntimeError(f'Cannot get the current version for {browser} browser')
    return version


def search_driver(browser='*', root='.'):
    driver_name = get_driver_name(browser)
    ext = '.exe' if platform == 'win32' else ''
    for path in Path(root).rglob(f'{driver_name}driver{ext}'):
        return path.absolute()


def get_os():
    if platform == 'win32':
        return 'win'
    elif platform == 'darwin':
        return 'mac'
    return platform  # linux


def get_os_default_browser():
    if platform == 'linux':
        return brw.get_linux_default_browser()
    elif platform == 'win32':
        return brw.get_windows_default_browser()
    elif platform == 'darwin':
        return brw.get_mac_default_browser()
    else:
        raise RuntimeError('Unknown operating system')
