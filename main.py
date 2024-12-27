import csv
from bs4 import BeautifulSoup
from selenium import webdriver

URL = 'https://www.amazon.com'


def get_url(search_text: str):
    """Generate a url from search text"""
    template = f'{URL}/s?k={{}}&ref=nb_sb_noss_1'
    search_term = search_text.replace(' ', '+')

    # add term query to url
    url = template.format(search_term)

    # add page query placeholder
    url += '&page={}'

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

    # keep chrome open after program finishes
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)

    # configure the webdriver
    driver = webdriver.Chrome(options=chrome_options)
    records = []
    url = get_url(search_term)

    for page in range(1, 21):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        for item in results:
            record = extract_record(item)
            if record:
                records.append(record)

    driver.close()

    # save data to csv file
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Description', 'Price', 'Rating', 'ReviewCount', 'Url'])
        writer.writerows(records)

    # run the main program


if __name__ == '__main__':
    main('ultrawide monitor')
