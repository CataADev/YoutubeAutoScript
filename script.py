import sys
import time

import numpy as np

from selenium import webdriver
from selenium.webdriver.common.by import By

# getting the driver
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
driver.get("https://youtube.com")

# accepting the cookies popup
acceptCookiesButton = driver.find_element(By.XPATH, '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/a/tp-yt-paper-button')
acceptCookiesButton.click()

time.sleep(2.5)

# searching for the video
searchBox = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/div/ytd-masthead/div[3]/div[2]/ytd-searchbox/form/div[1]/div[1]/input')

if len(sys.argv) > 1:
    searchText = str(sys.argv[1])
    print(searchText)
    searchBox.send_keys(searchText)
else:
    searchBox.send_keys('Cat Videos')

searchBox.submit()
