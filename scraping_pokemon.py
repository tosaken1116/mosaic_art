import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def scrapingPokemon() :
    url = "https://zukan.pokemon.co.jp/#item001"
    driver = open_url_link(url)
    images = driver.find_elements(By.CLASS_NAME,"loadItem")
    for index, image in enumerate(images):
        img_tag = image.find_element(By.TAG_NAME,'img')
        src = img_tag.get_attribute("src")
        if src:
            with open(f"./pokemon_png/{index}.png",'wb') as f:
                f.write(img_tag.screenshot_as_png)

def open_url_link(url):
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    option.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=option)
    driver.get(url)
    while BeautifulSoup(driver.page_source,"html.parser").find('img',alt='ラブトロス') is None:
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.5)
    driver.save_screenshot("test.png")
    return driver

scrapingPokemon()