from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time


class MemeScraper:
    meme_URL = 'https://imgflip.com/ai-meme'
    meme_index = {}
    ImageLink = None
    driver = None

    def updateImage(self):
        driver = self.driver
        driver.get(self.meme_URL)

        time.sleep(3)

        driver.find_element(By.CLASS_NAME, 'aim-generate-btn').click()
        time.sleep(1)
        self.ImageLink = driver.find_element(By.CLASS_NAME,
                                             'img-code').get_attribute("value")

    def initiateDriver(self):
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(
            options=options,
            executable_path='geckodriver.exe')
        driver.implicitly_wait(30)
        driver.set_window_size(1920, 1080)
        driver.get(self.meme_URL)
        self.driver = driver

    def update_available_memes(self):
        req = requests.get(self.meme_URL)
        # print(req.text)
        soup = BeautifulSoup(req.text, "html.parser")
        t = soup.find_all(class_="aim-meme-btn")
        for button in t:
            memeName = button.find("img").get("title")
            memeIndex = button.get("data-index")
            self.meme_index[memeIndex] = memeName

    def __init__(self) -> None:
        self.update_available_memes()
        self.initiateDriver()

    def __del__(self):
        self.driver.quit()


# m = MemeScraper()
# m.updateImage()
# print(m.ImageLink)
