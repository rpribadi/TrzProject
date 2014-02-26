import errno
import csv
import math
import re
import requests
import time
import os

from urllib2 import urlopen
from bs4 import BeautifulSoup

BASE_URL = "http://www.imdb.com/"
SEARCH_URL = BASE_URL + "search/title?at=0&sort=moviemeter,asc&start=%s&title_type=feature&year=%s,%s"
OUTPUT_FILE = "main_%s_page_%s.csv"
RECORD_PER_PAGE = 50


class Record:
    def __init__(self, row):
        self.row = row

    def get_id(self):
        return self.row.find("a").get("href")[1:]

    def get_title(self):
        return self.row.find("a").get_text().strip().encode("utf-8")

    def get_url(self):
        return self.row.find("a").get("href")

    def get_rating(self):
        rating = self.row.find("span", {"class": "v"}).get_text().strip()
        return int(re.sub(r'[^\x00-\x7F]+', '', rating))

    def get_date(self):
        date = self.row.find("span", {"class": "a"})
        if not date:
            return None
        return date.find("span").get("title")

    def get_size(self):
        # Always in MB
        _ = self.row.find("span", {"class": "s"})
        if not _:
            return None
        _ = _.get_text().strip().split()
        size = int(_[0])
        unit = _[1]
        if unit == "GB":
            size = size * 1024
        return size

    def get_seeder(self):
        seeder = self.row.find("span", {"class": "u"}).get_text().strip()
        return int(seeder.replace(",", ""))

    def get_leecher(self):
        leecher = self.row.find("span", {"class": "d"}).get_text().strip()
        return int(leecher.replace(",", ""))

    def get_data(self):
        return [
            self.get_id(),
            self.get_title(),
            self.get_url(),
            self.get_rating(),
            self.get_date(),
            self.get_size(),
            self.get_seeder(),
            self.get_leecher()
        ]


def get_total_page(year):
    try:
        url = SEARCH_URL % (0, year, year)
        print "[STATUS] Connecting to URL: %s." % url
        webpage = urlopen(url).read()
    except Exception, e:
        print "[ERROR] Can't connect to URL: %s. Reason: %s." % (url, e)
        return 0
    else:
        print "[STATUS] Connected. Parsing URL content."
        soup = BeautifulSoup(webpage.decode('utf-8', 'ignore'))
        _ = soup.find("div", {"class": "leftright"}).find("div", {"id": "left"}).get_text().strip();
        total_record = int(re.search(r"of (?P<total>[0-9,]+)\s*titles", _).group('total').replace(",", ""))
        return math.ceil(total_record/RECORD_PER_PAGE)
        

def get_soup_page(url):
    try:
        print "[STATUS] Connecting to URL: %s." % url
        #webpage = urlopen(url).read()
        webpage = requests.get(url).text
    except Exception, e:
        print "[ERROR] Can't connect to URL: %s. Reason: %s." % (url, e)
        return None
    else:
        print "[STATUS] Connected. Parsing URL content."
        return BeautifulSoup(webpage.encode('utf-8'))

def run(year, from_page, to_page):

    output_file = os.path.join("results", "movie", year, OUTPUT_FILE)
    create_folder(output_file)

    page_number = 0 
    total = 0
    for page_number in range(from_page, to_page):
        start_at = 1 + page_number * RECORD_PER_PAGE
        url = SEARCH_URL % (start_at, year, year)
        time.sleep(2)
        soup = get_soup_page(url)

        rows = soup.find("table", {"class": "results"}).find_all('tr')

        with open(output_file % (year, page_number), "w") as f:
            writer = csv.writer(f, delimiter=';', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)

            for row in rows[1:3]:
                time.sleep(2)
                detail_url = row.find("td", {"class": "title"}).find("a").get("href")
                detail_soup = get_soup_page(BASE_URL + detail_url)
                #movie = Movie(detail_soup)
                #cast = Cast(detail_soup)
                release_url = detail_soup.find("h4", text="Release Date:").findNext("span").find("a").get("href")
                print release_url
                #release_date = ReleaseDate(get_soup_page(release_url))

#                     record = Record(row)
#                     print " - Parsed: %s" % record.get_title()
#                     writer.writerow(record.get_data())
                total += 1
                print "[STATUS] Sleeping .."

        print "[STATUS] Page Sleeping .."
        time.sleep(5)

    print "[STATUS] Parsing %s pages done. Total: %s." % (page_number, total)


def create_folder(output_file):
    path = os.path.dirname(output_file)
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


if __name__ == "__main__":
    # Number of movies is hardcoded for now
    for year in ["2011", "2012", "2013"]:
        total_page = get_total_page(year)
        run(year, 0, 1)
        print "[STATUS] Long sleeping ......"
        time.sleep(60)
