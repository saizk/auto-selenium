import json
import urllib.request
import subprocess
from sys import platform


LATEST_RELEASES = {
    'chrome': 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE',
    'firefox': 'https://api.github.com/repos/mozilla/geckodriver/releases/latest',
    'opera': 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases/latest',
    'edge': 'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/'
}
LATEST_RELEASES['brave'] = LATEST_RELEASES['chrome']

BROWSER_REGISTRY_PATHS = {
    'chrome': r'Software\Google\Chrome\BLBeacon',
    'firefox': r'Software\Mozilla\Mozilla Firefox',
    'edge': r'Software\Microsoft\Edge\BLBeacon',
    'brave': r'Software\BraveSoftware\Brave-Browser\BLBeacon'
}

MAC_BROWSER_PATHS = {
    'chrome': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    'firefox': '/Applications/Firefox.app/Contents/MacOS/firefox',
    'opera': '/Applications/Opera.app/Contents/MacOS/Opera',
    'brave': '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
}


def get_chromium_latest_release(driver, current_version=False):
    api_path = LATEST_RELEASES[driver]

    if current_version:
        version = get_browser_version(driver)
        api_path += f'_{version.split(".")[0]}' if version else ''

    with urllib.request.urlopen(api_path) as response:
        version = response.readlines()[0].decode('utf-8')

    return version


def get_browser_version(browser):
    if platform == 'linux':
        with subprocess.Popen(['chromium-browser', '--version'], stdout=subprocess.PIPE) as proc:
            process = proc.stdout.read().decode('utf-8')
            version = ''.join(filter(lambda char: char.isdigit() or char == '.', process)).strip()
    elif platform == 'darwin':
        process = subprocess.Popen([MAC_BROWSER_PATHS[browser], '--version'],
                                   stdout=subprocess.PIPE).communicate()[0].decode('UTF-8')
        version = ''.join(filter(lambda char: char.isdigit() or char == '.', process)).strip()
    else:  # win32
        version = get_browser_version_windows(browser)
    return version


def get_browser_version_windows(browser):
    assert platform == 'win32'
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, BROWSER_REGISTRY_PATHS[browser], 0, winreg.KEY_READ)
        name = 'version' if browser != 'firefox' else 'CurrentVersion'
        version = winreg.QueryValueEx(key, name)[0]
    except KeyError:
        raise RuntimeError(f'Cannot detect current version for {browser.title()} browser')
    return version


def get_github_latest_release(browser):  # for firefox and opera
    api_path = LATEST_RELEASES[browser]
    with urllib.request.urlopen(api_path) as response:
        version = json.loads(response.read())['tag_name']
    return version


def get_edge_latest_release():
    api_path = LATEST_RELEASES['edge']
    with urllib.request.urlopen(api_path) as response:
        html_str = response.readlines()[-1].decode('utf-8')

        versions_idx = html_str.find('Version: ')
        final_idx = html_str[versions_idx:].find(f'OS {platform}') + versions_idx
        init_idx = html_str[:final_idx].rfind('version') + 7

        version = html_str[init_idx: final_idx].strip()

    return version


def get_linux_default_browser():
    assert platform == 'linux'
    try:
        import re, subprocess
        def_list = subprocess.check_output(['cat', '/usr/share/applications/defaults.list']).decode('utf-8')
        default_browser = re.findall("http=([^\.]*)", def_list)[0].split('-')[0]

        if default_browser == 'google':
            default_browser = 'chrome'

    except Exception:
        return 'firefox'  # linux default

    return default_browser


def get_windows_default_browser():
    assert platform == 'win32'
    try:
        import winreg
        key = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
                             r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice')
        prog_id, _ = winreg.QueryValueEx(key, 'ProgId')
        key = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE),
                             rf'SOFTWARE\Classes\{prog_id}\shell\open\command')
        launch_string, _ = winreg.QueryValueEx(key, '')  # read the default value
        def_browser_path = launch_string.lower().rstrip()

        for key in ['chrome', 'firefox', 'opera', 'edge', 'brave']:
            if key in def_browser_path:
                return key

        raise RuntimeError(f'Default browser not found or not supported: {def_browser_path}')

    except FileNotFoundError:  # Just when Opera default browser
        return 'opera'


def get_mac_default_browser():
    assert platform == 'darwin'
    return NotImplementedError('Mac default browser function not implemented yet')

