from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import asyncio
from selenium.webdriver.firefox.service import Service


class MemeScraper:
    #meme_URL: str = 'https://imgflip.com/ai-meme'
    meme_index_dict: dict = {}
    driver: driver = None
    producing_meme = False

    def __init__(self, meme_URL: str = 'https://imgflip.com/ai-meme', queue_max_size: int = 5, queue_refresh_threshold: int = 2) -> None:
        self.queue_max_size = queue_max_size
        self.queue_refresh_threshold = queue_refresh_threshold
        self.meme_URL = meme_URL
        self.initiateDriver()
        self.update_available_memes()
        self.intilializeQueue(self.queue_max_size,
                              self.queue_refresh_threshold)
        self.StartMemeProducer()

    def intilializeQueue(self, queue_max_size, queue_refresh_threshold) -> None:
        self.queue_refresh_threshold = queue_refresh_threshold
        self.meme_queue = asyncio.Queue(maxsize=queue_max_size)

    def StartMemeProducer(self):
        #print("start accessed")
        asyncio.create_task(self.memeProducer())

    async def memeProducer(self) -> None:
        meme_queue = self.meme_queue
        if meme_queue.qsize() <= self.queue_refresh_threshold and not self.producing_meme:
            self.producing_meme = True
            while not meme_queue.full():
                await asyncio.sleep(3)
                print("producer starting")
                new_meme = await self.produceMeme()
                await meme_queue.put(new_meme)
                print("producer done")
            self.producing_meme = False
        print("producer shutting down")

    async def getMeme(self) -> str:
        print("getting meme")
        print(self.meme_queue)
        meme = await self.meme_queue.get()
        self.meme_queue.task_done()
        self.StartMemeProducer()
        return meme

        # Expand to other sites
        # getMemeStrategy at some point?
    async def produceMeme(self, meme_index: int = None) -> None:
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

    def listAvailableMemes(self) -> dict:
        return self.meme_index_dict

    def initiateDriver(self):
        options = Options()
        options.headless = True
        service = Service(executable_path='geckodriver.exe',
                          log_path="nul")
        driver = webdriver.Firefox(
            options=options,
            service=service
            # executable_path='geckodriver.exe',
            # service_log_path="nul"
        )
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

    def __del__(self):
        try:
            self.driver.close()
            self.driver.quit()

        except:
            print("could not quit driver")


async def main():
    m = MemeScraper(queue_max_size=10, queue_refresh_threshold=4)
    # while True:
    await asyncio.sleep(30)
    print(await m.getMeme())
    print(await m.getMeme())
    print(await m.getMeme())
    print(await m.getMeme())
    print(await m.getMeme())
    print(await m.getMeme())
    print(await m.getMeme())

if __name__ == "__main__":
    asyncio.run(main())

    # # m.produceMeme()
    # messages = '\n'.join([f"{k} : {v}" for k,
    #                       v in m.meme_index_dict.items()])
    # print(messages)
