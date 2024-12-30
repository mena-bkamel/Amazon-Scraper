import csv

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

URL = 'https://www.amazon.com'


def chrome_webdriver():
    # keep chrome open after program finishes
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    # user_agent = fake_useragent()
    # chrome_options.add_argument(f"user-agent={user_agent}")

    # configure the webdriver
    driver = webdriver.Chrome(options=chrome_options)

    return driver


def search_for_product(driver: chrome_webdriver):
    search_bar = driver.find_element(By.ID, "e")
    search_bar.send_keys("ultrawide monitor")
    search_bar.send_keys(Keys.RETURN)


def next_page(driver: chrome_webdriver):
    try:
        a_tag = driver.find_element(by=By.LINK_TEXT, value="Next")
        url = f"{a_tag.get_attribute("href")}"
        return url
    except NoSuchElementException:
        print("No More pages to scrap")
        driver.close()


def get_url(search_text: str):
    """Generate a url from search text"""
    template = f'{URL}/s?k={{}}&ref=cs_503_search'
    search_term = search_text.replace(' ', '+')
    # add term query to url
    url = template.format(search_term)

    return url


def extract_record(item):
    """Extract and return data from a single record"""

    # description and url
    a_tag = item.find('a', class_='a-link-normal s-line-clamp-2 s-link-style a-text-normal')
    url = f"{URL}{a_tag.get('href')}"
    description = item.h2.text

    try:
        # product price
        price_parent = item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text

    except AttributeError:
        return

    try:
        # rating and review count
        rating = item.i.text
        review_count = item.find('span', {'class': 'a-size-base s-underline-text'}).text

    except AttributeError:
        rating = ''
        review_count = ''

    result = (description, price, rating, review_count, url)

    return result


def main(search_term):
    """Run main program routine"""

    records = []
    url = get_url(search_term)
    driver = chrome_webdriver()

    driver.get(url)
    search_for_product(driver)

    next_page_url = next_page(driver)

    while next_page_url:

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        for item in results:
            record = extract_record(item)
            if record:
                records.append(record)

        # save data to csv file
        with open('results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Description', 'Price', 'Rating', 'ReviewCount', 'Url'])
            writer.writerows(records)

        driver.get(next_page_url)
        next_page_url = next_page(driver)


if __name__ == '__main__':
    main('ultrawide monitor')
