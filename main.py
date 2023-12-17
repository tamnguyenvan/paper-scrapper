import json
import csv
import time
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def find_element(driver, xpath: str, timeout: int = 20):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except:
        return


def scrape_papers(driver, papers, start_index: int = 0):
    xpath = '//*[@id="listing-main"]'
    main_list = find_element(driver, xpath)
    if not main_list:
        print('Main list not found')
        return []

    new_papers = dict()
    xpath_list_box_elements = './/div[contains(@class, "list-box")]'
    list_box_elements = main_list.find_elements(By.XPATH, xpath_list_box_elements)

    list_box_elements = list_box_elements[start_index:]
    for list_box_element in list_box_elements:

        xpath_list_conf = './/a[@class="list-conf "]'
        link_element = list_box_element.find_element(By.XPATH, xpath_list_conf)
        link = link_element.get_attribute('href')

        xpath_list_title = './/div[@class="list-title"]'
        title_element = list_box_element.find_element(By.XPATH, xpath_list_title)
        title = title_element.text

        xpath_list_ref = './/div[@class="list-reference"]'
        ref_element = list_box_element.find_element(By.XPATH, xpath_list_ref)
        reference = ref_element.text

        title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
        if title_hash not in papers:
            paper_info = {'title': title, 'link': link, 'reference': reference}
            new_papers[title_hash] = paper_info
    return new_papers


def scroll_down(driver):
    scroll_height = 15000

    print('sh', scroll_height)
    driver.execute_script(f"window.scrollTo(0, {scroll_height});")


def main():
    url = 'https://eposters.ddw.org/ddw/#!*menu=16*browseby=8*sortby=2*ce_id=2482*ot_id=27743*trend=19514*marker=4154'
    driver = webdriver.Chrome()

    driver.get(url)

    max_scrolls = 500
    papers = dict()

    start_index = 0
    for i in range(max_scrolls):
        print(f'Scanning window view #{i+1}...')

        papers_per_screen_view = scrape_papers(driver, papers, start_index)
        if papers_per_screen_view:
            # for paper in papers_per_screen_view:
            #     print(paper)

            print(f'{len(papers_per_screen_view)} new papers found')

            start_index += len(papers_per_screen_view)
            print(f'Increasing index to {start_index}')

            papers.update(papers_per_screen_view)

            scroll_down(driver)
            time.sleep(5)
        else:
            print('No paper found. Terminating...')
            break

    # Save scapped data
    save_path = 'papers.csv'
    with open(save_path, 'w') as f:
        writer = csv.writer(f, quotechar='"')
        for _, paper_info in papers.items():
            writer.writerow([paper_info['title'], paper_info['link'], paper_info['reference']])

    print(f'Saved results as {save_path}')


if __name__ == '__main__':
    main()