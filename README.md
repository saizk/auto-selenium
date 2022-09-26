# auto-selenium
![PyPI version](https://img.shields.io/pypi/v/auto-selenium)

Auto-Selenium is a Python tool to automate the download of Selenium Web Drivers and store the profile sessions for the following browsers:
* Google Chrome
* Firefox
* Opera
* Brave
* Edge (only for Windows)

It utilizes Selenium and MSEdge tools

## Quickstart examples
### Installation
```Python
pip install auto-selenium
```

### Simple Usage
```Python
from autoselenium import Driver

driver = Driver('chrome')  # downloads driver based on current version of the browser
driver.get('https://www.google.com/')
```

### Context Manager
```Python
with Driver('brave', root='drivers') as driver:  # equivalent to Selenium's WebDriver object
    driver.get('https://www.github.com/saizk')
    # Selenium Webdriver command examples
    driver.find_elements_by_tag_name('div')
    driver.refresh()
```

### Download specific versions of each driver
```Python
from autoselenium import download_driver, get_version

download_driver('firefox', version='0.29.1', root='drivers')
download_driver('opera', 'latest')

cversion = get_version('brave', 'current')
lversion = get_version('brave', 'latest')

if cversion < lversion:
    print('You should update your browser!')
```
You can specify between 'current', 'latest' or input an specific version for a driver.

### Create your custom driver
```Python
import autoselenium

class TwitterBot(autoselenium.Driver):
    
    _URL = 'https://twitter.com'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logged = False
    
    def log(self):
        self.logged = True
        pass
    
    def scrape(self):
        pass
```
## Contribute
Would you like to contribute to this project? Here are a few starters:
- Improve documentation
- Add Testing examples
- Bug hunts and refactor
- Additional features/ More integrations
- Phantom JS support
- Implement default browser functions for Mac 
