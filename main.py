import errno
import csv
import re
import time
import os

from urllib2 import urlopen
from bs4 import BeautifulSoup

BASE_URL = "http://torrentz.eu"
SEARCH_URL = BASE_URL + "/verifiedP?f=movies+"
OUTPUT_FILE = "main_%s_page_%s.csv"


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


def run(year):
    output_file = os.path.join("results", year, OUTPUT_FILE)
    create_folder(output_file)

    page_number = 0
    url = ""
    total = 0
    while(True):
        try:
            url = "%s%s&p=%s" % (SEARCH_URL, year, page_number)
            print "[STATUS] Connecting to URL: %s." % url
            webpage = urlopen(url).read()
        except Exception, e:
            print "[ERROR] Can't connect to URL: %s. Reason: %s." % (url, e)
            break
        else:
            print "[STATUS] Connected. Parsing URL content."
            soup = BeautifulSoup(webpage.decode('utf-8', 'ignore'))
            rows = soup.find("div", {"class": "results"}).find_all('dl')

            if len(rows) == 1:
                text = rows[0].find("dt").get_text().strip()
                if text == "No Torrents yet":
                    print "[STATUS] Page is empty. Exit."
                    break
            with open(output_file % (year, page_number), "w") as f:
                writer = csv.writer(f, delimiter=';', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)

                for row in rows:
                    record = Record(row)
                    print " - Parsed: %s" % record.get_title()
                    writer.writerow(record.get_data())
                    total += 1

        page_number += 1
        print "[STATUS] Sleeping .."
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
    for year in ["2011", "2012", "2013"]:
        run(year)
        print "[STATUS] Long sleeping ......"
        time.sleep(60)
