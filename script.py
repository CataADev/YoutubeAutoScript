import sys
import time
import logging

# import cv2
# import numpy as np
# import pyautogui

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


# Configuring the logging
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename = "logfile.log",
                    filemode = "w",
                    format = LOG_FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# configuring the driver
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# options.add_argument("--start-maximized") # to start in fullscreen

# getting the driver
driver = webdriver.Chrome(options=options)
driver.get("https://youtube.com")

# accepting the cookies popup, if one appears
try:
    acceptCookiesButton = driver.find_element(By.XPATH, '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/a/tp-yt-paper-button')
    acceptCookiesButton.click()
except NoSuchElementException:
    pass

# time delay is needed to wait for the page to load
time.sleep(1.5)

# searching for the video
searchBox = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/div/ytd-masthead/div[3]/div[2]/ytd-searchbox/form/div[1]/div[1]/input')
SEARCH_TEXT = ""

if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        SEARCH_TEXT += str(sys.argv[i]) + " "
    logger.info("Searched for: %s", SEARCH_TEXT)
else:
    SEARCH_TEXT = "Funny Videos"
    logger.info("Searched for: %s (default)", SEARCH_TEXT)

searchBox.send_keys(SEARCH_TEXT)
searchBox.send_keys(Keys.ENTER)

time.sleep(1)

searchedVideo = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/ytd-thumbnail/a/yt-img-shadow/img')
searchedVideo.click()

time.sleep(0.5)

youtubeVideo = driver.find_element(By.XPATH,'/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div/div/div/ytd-player/div/div')


while 'ad-showing' in youtubeVideo.get_attribute('class').split() and 'paused-mode' not in youtubeVideo.get_attribute('class').split():
    print('Ad is showing')
    time.sleep(0.5)
    try:
        adDuration = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div/div/div/ytd-player/div/div/div[17]/div/div[3]/div/div[1]/span/div').text
        print('Skippable Ad after ' + adDuration + 's')
        time.sleep(int(adDuration) + 0.5)
        skipButton = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div/div/div/ytd-player/div/div/div[17]/div/div[3]/div/div[2]/span/button')
        skipButton.click()
        print('Ad Skipped')
    except NoSuchElementException:
        adDuration = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div/div/div/ytd-player/div/div/div[17]/div/div[2]/span[2]/div').text.split(":")[1]
        print('Unskippable Ad of ' + adDuration + 's')
        time.sleep(int(adDuration) + 0.5)

driver.quit()
