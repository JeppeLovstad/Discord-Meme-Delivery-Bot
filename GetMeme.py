from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class MemeScraper:
    meme_URL: str = 'https://imgflip.com/ai-meme'
    meme_index_dict: dict = {}
    driver: driver = None

    def updateImage(self, meme_index: int = None, ) -> str:
        driver = self.driver
        driver.get(self.meme_URL)
        meme_number = len(self.meme_index_dict)-1

        # Get random meme, if not specified
        if not meme_index or meme_index > meme_number or meme_index < 0:
            meme_index = random.randint(0, meme_number)

        self.checkLoading(By.ID, "site-loading")

        driver.find_element(
            By.CSS_SELECTOR, f"div[data-index='{meme_index}']").click()

        self.checkLoading(By.ID, "site-loading")

        driver.find_element(By.CLASS_NAME, 'aim-generate-btn').click()

        self.checkLoading(By.CLASS_NAME, "img-code", True)

        return driver.find_element(By.CLASS_NAME,
                                   'img-code').get_attribute("value")

    def getAvailableMemes(self) -> dict:
        return self.meme_index_dict

    def initiateDriver(self):
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(
            options=options,
            executable_path='geckodriver.exe')
        driver.implicitly_wait(0)
        driver.set_window_size(1920, 1080)
        # driver.get(self.meme_URL)
        self.driver = driver

    def checkLoading(self, by: By, locator, stop_when_found: bool = False):
        driver = self.driver
        try:
            # wait for loading element to appear
            # - required to prevent prematurely checking if element
            #   has disappeared, before it has had a chance to appear
            WebDriverWait(driver, 5
                          ).until(EC.presence_of_element_located((by, locator)))

            # then wait for the element to disappear
            if not stop_when_found:
                WebDriverWait(driver, 30
                              ).until_not(EC.presence_of_element_located((by, locator)))

        except TimeoutException:
            # if timeout exception was raised - it may be safe to
            # assume loading has finished, however this may not
            # always be the case, use with caution, otherwise handle appropriately.
            pass

    def update_available_memes(self):
        req = requests.get(self.meme_URL)
        soup = BeautifulSoup(req.text, "html.parser")
        t = soup.find_all(class_="aim-meme-btn")
        for button in t:
            memeName = button.find("img").get("title")
            memeIndex = button.get("data-index")
            self.meme_index_dict[memeIndex] = memeName

    def __init__(self) -> None:
        self.initiateDriver()
        self.update_available_memes()

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

# m = MemeScraper()
# # m.updateImage()
# messages = '\n'.join([f"{k} : {v}" for k,
#                       v in m.meme_index_dict.items()])
# print(messages)
