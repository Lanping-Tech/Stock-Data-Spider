from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from spider import get_driver, get_base_info
driver = get_driver()

print(get_base_info(driver, 
                    '000983',
                    {'read': '289', 'subcomments': '1', 'comment_url': '/news,000983,1085059599.html'}))

driver.quit()