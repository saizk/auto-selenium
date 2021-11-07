# -*- coding: utf-8 -*-

import os
import shutil
import urllib.request
from urllib.error import HTTPError, URLError

from autoselenium.utils import *

__all__ = ['download_driver', 'download_default_driver', 'get_version']


def download_driver(driver, version='current', root='.'):
    if not os.path.exists(root):
        os.mkdir(root)

    driver_folder = f'{root}/{driver}'
    driver_path = driver_folder + f'/{driver}driver' + ('.exe' if platform == 'win32' else '')
    driver_path = Path(driver_path).absolute()

    if driver_path.exists():
        return
    try:
        version = get_version(driver, version)
        url, filename = gen_url(driver, version)
        download_url(url, filename)
        extract(filename, driver_folder)
        fix_paths(driver, driver_path)
        assert driver_path.exists()

    except (HTTPError, URLError):
        raise RuntimeError(f'Cannot download {driver} driver.\n'
                           f'If the problem persist, download the driver manually.')

    return driver_path


def download_default_driver(root='.'):
    return download_driver(get_os_default_browser(), root=root)


def get_version(driver, version):
    if version == 'latest':
        return get_latest_version(driver)
    elif version == 'current':
        return get_current_version(driver)
    else:
        return parse_version(driver, version)


def parse_version(driver, raw_version):
    # version = ''.join(filter(lambda char: char.isdigit() or char == '.', raw_version))
    if driver == 'firefox':
        return 'v' + raw_version
    elif driver == 'opera':
        return 'v.' + raw_version
    else:
        return raw_version


def download_url(url, filename):
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def extract(filename, tgt_path):
    shutil.unpack_archive(filename, tgt_path)
    os.remove(filename)


def fix_paths(driver, driver_path):
    src_path = search_driver(root=driver_path.parent)
    if driver in ['firefox', 'brave', 'edge']:
        os.rename(src_path, driver_path)      # rename for convenience
        if driver == 'edge':
            shutil.rmtree(f'{driver_path.parent}/Driver_Notes')

    elif driver == 'opera':
        shutil.move(src_path, driver_path)  # moves driver and deletes extra dir
        shutil.rmtree(src_path.parent)

    if platform in ['linux', 'darwin'] and driver in ['chrome', 'opera', 'brave']:
        os.chmod(driver_path, 755)  # add permissions for linux/mac drivers
