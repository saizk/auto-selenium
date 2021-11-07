# -*- coding: utf-8 -*-

from sys import platform
from pathlib import Path
from jinja2 import Template

import autoselenium.browsers as brw


DRIVER_URLS = {
    'chrome': 'https://chromedriver.storage.googleapis.com/{{version}}/chromedriver_{{os}}{{bits}}.{{format}}',
    'firefox': 'https://github.com/mozilla/geckodriver/releases/download/{{version}}/geckodriver-{{version}}-{{os}}{{bits}}.{{format}}',
    'opera': 'https://github.com/operasoftware/operachromiumdriver/releases/download/{{version}}/operadriver_{{os}}{{bits}}.{{format}}',
    'edge': 'https://msedgedriver.azureedge.net/{{version}}/edgedriver_{{os}}{{bits}}.{{format}}',
    # 'edge': 'https://msedgedriver.azureedge.net/{{version}}/edgedriver_win{{bits}}.{{format}}'
}
DRIVER_URLS['brave'] = DRIVER_URLS['chrome']


def gen_url(driver, version):

    if platform == 'win32' and driver in ['chrome', 'brave']:
        bits = 32
    elif platform == 'darwin' and driver == 'firefox':
        bits = 'os'
    else:
        bits = 64

    if platform in ['linux', 'darwin'] and driver == 'firefox':
        file_ext = 'tar.gz'
    else:
        file_ext = 'zip'

    template = Template(DRIVER_URLS[driver])
    url = template.render(version=version, os=get_os(), bits=bits, format=file_ext)
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
    ext = '.exe' if platform == 'win32' else ''
    for path in Path(root).rglob(f'{browser}driver{ext}'):
        return path.absolute()


def get_os():
    if platform == 'win32':
        return 'win'
    elif platform == 'darwin':
        return 'mac'
    else:
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
