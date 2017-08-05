import csv
import logging
import os
import re
import sys
from datetime import datetime

from selenium import webdriver

# for python2 use encode("utf-8") for text

logger = logging.getLogger("wscrapper")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

driver = webdriver.PhantomJS()
driver.maximize_window()
curr_date = datetime.now().strftime("%Y-%m-%d")

# files
os.makedirs(curr_date, exist_ok=True)
band_links = "./{0}/band_links.csv".format(curr_date)
band_details = "./{0}/band_details.csv".format(curr_date)
album_links = "./{0}/album_links.csv".format(curr_date)
album_details = "./{0}/album_details.csv".format(curr_date)
member_links = "./{0}/member_links.csv".format(curr_date)
similar_bands = "./{0}/similar_bands.csv".format(curr_date)


# should run first
def get_bands_links():
    driver.get("http://metalstorm.net/bands/index2.php")
    bands = driver.find_elements_by_css_selector('#page-content table a')
    with open(band_links, 'w') as f:
        writer = csv.writer(f)
        for band in bands:
            row = [band.text, band.get_attribute('href')]
            writer.writerow(row)
            logger.info("add band_link %s", row)


def get_band_details():
    with open(band_details, 'w') as f:
        writer = csv.writer(f)
        for band_detail_type in [
            ("country", "country"),
            ("bandname", "also_known_as"),
            ("label", "labels"),
            ("year_formed", "former_in"),
            ("year_disbanded", "disbanded_in"),
            ("style", "style")
        ]:
            for detail in driver.find_elements_by_xpath(
                    "//table[@class='break-on-xs']//tr[./td/a[contains(@href, '{0}')]]//a".format(band_detail_type[0])):
                row = [driver.current_url, detail.get_property("textContent"),
                       detail.get_attribute('href'),
                       band_detail_type[1]]
                writer.writerow(row)
                logger.info("add band_detail %s", row)


def get_similar_bands():
    with open(similar_bands, 'w') as f:
        writer = csv.writer(f)
        for similar in driver.find_elements_by_css_selector("#similar_bands a[href *= 'band.php']"):
            row = [driver.current_url, similar.get_property("textContent"),
                   similar.get_attribute('href')]
            writer.writerow(row)
            logger.info("add similar_bands %s", row)


def get_band_lineup():
    with open(member_links, 'w') as f:
        writer = csv.writer(f)
        for lineup_type in [
            ("lineuptab0", "current members"),
            ("lineuptab1", "studio musicians"),
            ("lineuptab2", "live musicians"),
            ("lineuptab3", "guest musicians"),
            ("lineuptab4", "former musicians")
        ]:
            for album in driver.find_elements_by_css_selector(
                    "#page-content #{0} a[href *= 'bandmember.php']".format(lineup_type[0])):
                row = [driver.current_url, album.get_property("textContent"),
                       album.get_attribute('href'),
                       lineup_type[1]]
                writer.writerow(row)
                logger.info("add member_link %s", row)


def get_album_links():
    with open(album_links, 'w') as f:
        writer = csv.writer(f)
        for album_type in [
            ("discotab1", "album"),
            ("discotab2", "ep"),
            ("discotab3", "other_release")
        ]:
            for album in driver.find_elements_by_css_selector(
                    "#page-content #{0} a[href *= 'album.php']".format(album_type[0])):
                row = [driver.current_url, album.get_property("textContent"),
                       album.get_attribute('href'),
                       album_type[1]]
                writer.writerow(row)
                logger.info("add album_link %s", row)


def get_album_details():
    with open(album_details, 'w') as f:
        writer = csv.writer(f)
        for album_details_type in [
            ("//tr[contains(.,'Release date')]/td[2]", "release_date"),
            ("//tr[contains(.,'Style')]/td[2]", "style"),
            ("//*[contains(@class,'discography-album')]//*[contains(@class,'left-col')]//img", "cover"),
            ("//*[contains(@class,'discography-album')]//*[contains(@id,'tracks')]", "tracks"),
            ("//*[contains(@class,'album-rating')]//*[contains(@class,'megarating')]", "rating"),
            ("//*[contains(@class,'album-rating')]//*[contains(@class,'votes_num')]", "votes_num")
        ]:
            for album in driver.find_elements_by_xpath(album_details_type[0]):
                p = 'textContent'
                if album_details_type[1] == 'cover':
                    p = 'src'
                val = album.get_property(p)
                if album_details_type[1] == 'votes_num':
                    val = re.search('\d+', str(val)).group()
                row = [driver.current_url, val, album_details_type[1]]
                writer.writerow(row)
                logger.info("add album_details %s", row)


def process_band_pages():
    with open(band_links, 'r') as b:
        band_count = sum(1 for _ in b)
    with open(band_links, 'r') as b:
        bands_processed = 0
        reader = csv.reader(b)
        for br in reader:
            if len(br) is 0:
                break
            driver.get(br[1])
            get_band_details()
            get_band_lineup()
            get_album_links()
            get_similar_bands()
            bands_processed += 1
            logger.info('complete band page processing [%s/%s]', bands_processed, band_count)


def process_album_pages():
    with open(album_links, 'r') as f:
        album_count = sum(1 for _ in f)
    with open(album_links, 'r') as f:
        album_processed = 0
        reader = csv.reader(f)
        for line in reader:
            driver.get(line[2])
            get_album_details()
            album_processed += 1
            logger.info('complete album page processing [%s/%s]', album_processed, album_count)


get_bands_links()
process_band_pages()
process_album_pages()

driver.close()
