import csv
import logging
import sys
from datetime import datetime
from selenium import webdriver


logger = logging.getLogger("wscrapper")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


driver = webdriver.PhantomJS()
curr_date = datetime.now().strftime("%Y-%m-%d")

# files
band_links = "band_links_{0}.csv".format(curr_date)
band_details = "band_details_{0}.csv".format(curr_date)
album_links = "album_links_{0}.csv".format(curr_date)
album_details = "album_details_{0}.csv".format(curr_date)


logger.info("start")


def get_bands_links():
    driver.get("http://metalstorm.net/bands/index2.php")
    bands = driver.find_elements_by_css_selector('#page-content table a')
    with open(band_links, 'w') as f:
        writer = csv.writer(f)
        for band in bands:
            row = [band.text.encode("utf-8"), band.get_attribute('href')]
            writer.writerow(row)
            logger.info("add band_link %s", row)


def get_album_links():
    with open(band_links, 'r') as b, open(album_links, 'w') as a:
        reader = csv.reader(b)
        aw = csv.writer(a)
        for br in reader:
            driver.get(br[1])
            # albums
            for i in driver.find_elements_by_css_selector("#page-content a[href *= 'album.php']"):
                row = [br[0], br[1], i.text.encode("utf-8"), i.get_attribute('href')]
                aw.writerow(row)
                logger.info("add album_link %s", row)


def init():
    driver.get("http://metalstorm.net/bands/index2.php")


init()
# get_bands_links()
get_album_links()


driver.close()
