# auto-selenium
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

with Driver('chrome', root='drivers') as driver:
    driver.get('https://www.google.com/')
    # Selenium Webdriver command examples
    driver.find_elements_by_tag_name('div')
    driver.refresh()
```
Downloads driver based on current version of the browser. When it is used as a context manager, the driver returns Selenium's WebDriver object.

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
    
    def login_required(func):
        def logged_checker(self, *args, **kwargs):
            if not self.logged:
                self.log()
            return func(self, *args, **kwargs)
        return logged_checker    
    
    def log(self):
        self.logged = True
        pass
    
    @login_required
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