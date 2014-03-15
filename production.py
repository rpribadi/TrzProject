import csv
import re
import time

from urllib2 import urlopen
from bs4 import BeautifulSoup

BASE_URL = "http://www.imdb.com/title/%s/"
INPUT_FILE = "movie_2013.csv"
OUTPUT_FILE = "production.csv"


class Production:
    def __init__(self, soup):
        table = soup.find("h4", text="Production Co:")
        if not table:
            self.rows = []
        else:
            self.rows = table.findNextSiblings("span", {"itemprop": "creator"})

    def get_id(self, index):
        return re.search(
            r"/company/(?P<id>\w+)?",
            self.rows[index].find("a").get('href')
        ).group("id")

    def get_name(self, index):
        return self.rows[index].find("span").get_text().strip().encode("utf-8")

    def get_data_at(self, index):
        return [
            self.get_id(index),
            self.get_name(index)
        ]

    def get_data(self):
        data = []
        index = 0
        while index < len(self.rows):
            data.append(self.get_data_at(index))
            index += 1
        return data


def run(input_file, output_file, start=0, end=None):
    total = 0
    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        writer = csv.writer(f_out, delimiter=';', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        reader = csv.reader(f_in, delimiter=';', quotechar='"')

        index = 0
        for row in reader:
            print "[STATUS] Index: ", index
            index += 1
            if index - 1 < start:
                print "[STATUS] Skipped"
                continue

            try:
                url = BASE_URL % row[0]
                print "[STATUS] Connecting to URL: %s." % url
                webpage = urlopen(url).read()
            except Exception, e:
                print "[ERROR] Can't connect to URL: %s. Reason: %s." % (url, e)
                break
            else:
                soup = BeautifulSoup(webpage.decode('utf-8', 'ignore'))
                production = Production(soup)
                print " - Parsed: %s" % production.get_data()
                writer.writerows(production.get_data())

            total += 1

            if not end is None and index >= end:
                break

            print "[STATUS] Sleeping .."
            time.sleep(2)

    print "[STATUS] Parsing production done. Total: %s." % (total)


if __name__ == "__main__":
    run(INPUT_FILE, OUTPUT_FILE)
