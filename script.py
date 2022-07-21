import sys
import time
import logging
import threading

# needed for video rec
import cv2
import numpy as np
import pyautogui

# needed for audio rec
import pyaudio
import wave

# needed for navigating a browser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# needed for joining the two
import ffmpeg


# Configuring the logging
LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(message)s"
logging.basicConfig(level=logging.INFO,
                    format=LOG_FORMAT,
                    handlers=[
                        logging.FileHandler("logfile.log"),
                        logging.StreamHandler(sys.stdout)
                    ])
logger = logging.getLogger()

# configuring the driver
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# options.add_argument("--start-maximized") # to start in fullscreen
driver = webdriver.Chrome(options=options)

driver.get("https://youtube.com")

# accepting the cookies popup, if one appears
try:
    acceptCookiesButton = driver.find_element(
        By.XPATH, '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/a/tp-yt-paper-button')
    logger.info("Cookies Pop-up Shown")
    acceptCookiesButton.click()
    logger.info("Cookies Pop-up Succesfully Accepted")
except NoSuchElementException:
    logger.info("Cookies Pop-up Not Shown")

# time delay is needed to wait for the page to load
time.sleep(1.5)

# searching for the video - form command line/default
searchBox = driver.find_element(
    By.XPATH, '/html/body/ytd-app/div[1]/div/ytd-masthead/div[3]/div[2]/ytd-searchbox/form/div[1]/div[1]/input')
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

searchedVideo = driver.find_element(
    By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/ytd-thumbnail/a/yt-img-shadow/img')
searchedVideo.click()

time.sleep(0.5)

youtubeVideo = driver.find_element(
    By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div/div/div/ytd-player/div/div')

# ad handling
while 'ad-showing' in youtubeVideo.get_attribute('class').split():
    logger.info('Ad is showing')
    time.sleep(0.5)
    try:
        adDuration = driver.find_element(
            By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div/div/div/ytd-player/div/div/div[17]/div/div[3]/div/div[1]/span/div').text
        logger.info('Skippable Ad after %ss', adDuration)
        time.sleep(int(adDuration) + 0.5)
        skipButton = driver.find_element(
            By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div/div/div/ytd-player/div/div/div[17]/div/div[3]/div/div[2]/span/button')
        skipButton.click()
        logger.info('Ad Skipped')
    except NoSuchElementException:
        adDuration = driver.find_element(
            By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div/div/div/ytd-player/div/div/div[17]/div/div[2]/span[2]/div').text.split(":")[1]
        logger.info('Unskippable Ad of %ss', adDuration)
        time.sleep(int(adDuration) + 1)

# Video recording


def videoRecord(RECORD_TIME):
    # Setting up the video recording process
    SCREEN_SIZE = tuple(pyautogui.size())
    codec = cv2.VideoWriter_fourcc(*"XVID")
    FILENAME = "output.avi"
    FPS = 24.0
    out = cv2.VideoWriter(FILENAME, codec, FPS, SCREEN_SIZE)

    timer = 0
    logger.info("Video recording started")
    while timer <= RECORD_TIME*FPS:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

        timer += 1

    out.release()
    cv2.destroyAllWindows()

# Audio recording


def audioRecord(RECORD_SECONDS):
    # Setting up the audio recording process
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 48000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = 'output.wav'

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=7,
                    as_loopback=True)

    frames = []

    timer = 0
    logger.info("Audio recording started")
    while timer <= int(RATE / CHUNK * RECORD_SECONDS):
        data = stream.read(CHUNK)
        frames.append(data)

        timer += 1

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


RECORD_TIME = 5

logger.info("Recording Started")

thread1 = threading.Thread(target=videoRecord, args=(RECORD_TIME,))
thread1.start()

thread2 = threading.Thread(target=audioRecord, args=(RECORD_TIME,))
thread2.start()

thread1.join()
thread2.join()

logger.info("Recording ended")

# joining the two recordings
input_video = ffmpeg.input('./output.avi')
input_audio = ffmpeg.input('./output.wav')
ffmpeg.concat(input_video, input_audio, v=1, a=1).output('./output.mp4').run()

logger.info("Recordings joined")

driver.quit()
