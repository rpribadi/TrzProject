import csv
import time

from urllib2 import urlopen
from bs4 import BeautifulSoup

BASE_URL = "http://www.imdb.com/name/%s/"
INPUT_FILE = "unique_celeb.csv"
OUTPUT_FILE = "celeb.csv"


class Celeb:
    def __init__(self, id, soup):
        self.id = id
        self.soup = soup

    def get_name(self):
        return (self.soup.find("span", {"itemprop": "name"})
                         .get_text()
                         .strip()
                         .encode("utf-8"))

    def get_birth_date(self):
        birth_date = self.soup.find("time", {"itemprop": "birthDate"})

        if not birth_date:
            return None

        return birth_date.get("datetime")

    def get_birth_place(self):
        birth_date = self.soup.find("time", {"itemprop": "birthDate"})

        if not birth_date:
            return None

        birth_place = birth_date.findNextSibling("a")

        if not birth_place:
            return None

        return birth_place.get_text().strip().encode("utf-8")

    def get_data(self):
        return [
            self.id,
            self.get_name(),
            self.get_birth_date(),
            self.get_birth_place()
        ]


def run(input_file, output_file, start=0, end=None):
    total = 0
    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        writer = csv.writer(f_out, delimiter=';', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        reader = csv.reader(f_in, delimiter=';', quotechar='"')

        index = 0
        for (celeb_id,) in reader:
            print "[STATUS] Index: ", index
            index += 1
            if index - 1 < start:
                print "[STATUS] Skipped"
                continue

            try:
                url = BASE_URL % celeb_id
                print "[STATUS] Connecting to URL: %s." % url
                webpage = urlopen(url).read()
            except Exception, e:
                print "[ERROR] Can't connect to URL: %s. Reason: %s." % (url, e)
                break
            else:
                soup = BeautifulSoup(webpage.decode('utf-8', 'ignore'))
                celeb = Celeb(celeb_id, soup)
                print " - Parsed: %s" % celeb.get_data()
                writer.writerow(celeb.get_data())

            total += 1

            if not end is None and index >= end:
                break

            print "[STATUS] Sleeping .."
            time.sleep(3)

    print "[STATUS] Parsing celebs done. Total: %s." % (total)


if __name__ == "__main__":
    run(INPUT_FILE, OUTPUT_FILE)
