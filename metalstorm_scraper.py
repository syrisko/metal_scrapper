import csv

from selenium import webdriver

driver = webdriver.PhantomJS()


def get_bands_links():
    driver.get("http://metalstorm.net/bands/index2.php")
    bands = driver.find_elements_by_css_selector('#page-content table a')
    with open("band_links", 'w') as f:
        writer = csv.writer(f)
        for band in bands:
            writer.writerow([band.text, band.get_attribute('href')])


def init():
    driver.get("http://metalstorm.net/bands/index2.php")


init()
get_bands_links()

driver.close()
