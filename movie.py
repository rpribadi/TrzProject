import errno
import csv
import math
import re
import sys
import time
import os

from urllib2 import urlopen
from bs4 import BeautifulSoup

BASE_URL = "http://www.imdb.com"
SEARCH_URL = BASE_URL + "/search/title?at=0&sort=moviemeter,asc&start=%s&title_type=feature&year=%s,%s"
OUTPUT_FILE = "%s_%s_page_%s.csv"
RECORD_PER_PAGE = 50


class Movie:
    def __init__(self, movie_id, soup):
        self.movie_id = movie_id
        self.soup = soup

    def get_id(self):
        return self.movie_id

    def get_title(self):
        return (self.soup.find("h1")
                         .find('span', {'class': 'itemprop'})
                         .get_text()
                         .strip()
                         .encode('utf-8'))

    def get_year(self):
        year = self.soup.find("h1").find('span', {'class': 'nobr'})

        if not year:
            return None

        return year.get_text().strip().replace("(", "").replace(")", "")

    def get_rating(self):
        rating = (self.soup
                      .find('div', {'class': ['titlePageSprite',
                                             'star-box-giga-star']}))
        if not rating:
            return None

        return rating.get_text().strip()

    def get_budget(self):
        details = self.soup.find('div', {'id': "titleDetails"})
        if not details:
            return None

        budget = details.find("h4", text="Budget:")
        if not budget:
            return None

        return budget.next.next.strip().encode("utf-8")

    def get_opening_weekend_gross(self):
        details = self.soup.find('div', {'id': "titleDetails"})
        if not details:
            return None

        gross = details.find("h4", text="Opening Weekend:")
        if not gross:
            return None

        gross = gross.next.next.strip()
        return gross.split()[0].encode("utf-8")

    def get_opening_weekend_country(self):
        details = self.soup.find('div', {'id': "titleDetails"})
        if not details:
            return None

        gross = details.find("h4", text="Opening Weekend:")
        if not gross:
            return None

        country = gross.next.next.strip()
        return country.split()[1].replace("(", "").replace(")", "")

    def get_opening_weekend_date(self):
        details = self.soup.find('div', {'id': "titleDetails"})
        if not details:
            return None

        gross = details.find("h4", text="Opening Weekend:")
        if not gross:
            return None

        gross = gross.find_next_sibling("span").get_text().strip()
        return (gross.replace("(", "")
                     .replace(")", "")
                     .encode("utf-8"))

    def get_gross(self):
        details = self.soup.find('div', {'id': "titleDetails"})
        if not details:
            return None

        gross = details.find("h4", text="Gross:")
        if not gross:
            return None

        return gross.next.next.strip().encode("utf-8")

    def get_gross_country(self):
        details = self.soup.find('div', {'id': "titleDetails"})
        if not details:
            return None

        gross = details.find("h4", text="Gross:")
        if not gross:
            return None

        country = gross.find_next_sibling("span").get_text().strip()
        return country.replace("(", "").replace(")", "")

    def get_gross_date(self):
        details = self.soup.find('div', {'id': "titleDetails"})
        if not details:
            return None

        gross = details.find("h4", text="Gross:")
        if not gross:
            return None

        gross = gross.find_next_sibling("span").find_next_sibling("span").get_text().strip()
        return (gross.replace("(", "")
                     .replace(")", "")
                     .encode("utf-8"))

    def get_runtime(self):
        runtime = (self.soup
                       .find('time', {'itemprop': "duration"}))
        if not runtime:
            return None

        return runtime.get_text().strip().split()[0]

    def get_mpaa(self):

        mpaa = self.soup.find('span', {'itemprop': "contentRating"})
        if not mpaa:
            return None

        return mpaa.get("content").strip()

    def get_country(self):
        details = self.soup.find('div', {'id': "titleDetails"})
        if not details:
            return None

        country = details.find("h4", text="Country:")
        if not country:
            return None

        return country.find_next_sibling("a").get_text().strip()

    def get_language(self):

        details = self.soup.find('div', {'id': "titleDetails"})
        if not details:
            return None

        language = details.find("h4", text="Language:")
        if not language:
            return None

        return language.find_next_sibling("a").get_text().strip().encode("utf-8")

    def get_data(self):
        return [
            self.get_id(),
            self.get_title(),
            self.get_year(),
            self.get_rating(),
            self.get_runtime(),
            self.get_budget(),
            self.get_opening_weekend_gross(),
            self.get_opening_weekend_country(),
            self.get_opening_weekend_date(),
            self.get_gross(),
            self.get_gross_country(),
            self.get_gross_date(),
            self.get_mpaa(),
            self.get_country(),
            self.get_language(),
        ]


class MovieGenre:
    def __init__(self, movie_id, soup):
        self.movie_id = movie_id
        self.soup = soup
        self.rows = []
        genres = None

        details = self.soup.find('div', {'id': "titleStoryLine"})
        if details:
            genres = details.find("h4", text="Genres:")
        if genres:
            self.rows = genres.find_next_siblings('a')

    def get_genre(self, index):
        return self.rows[index].get_text().strip()

    def get_data_at(self, index):
        return [
            self.movie_id,
            self.get_genre(index)
        ]

    def get_data(self):
        data = []
        index = 0
        while index < len(self.rows):
            data.append(self.get_data_at(index))
            index += 1
        return data


class MovieDirector:
    def __init__(self, movie_id, soup):
        self.movie_id = movie_id
        details = soup.find("div", {"id": "title-overview-widget"})
        table = None
        if details:
            table = details.find("h4", text=re.compile(r"Director[s]{0,1}:"))
        if not table:
            self.rows = []
        else:
            self.rows = table.find_next_siblings("a", {'itemprop': 'url'})

    def get_id(self, index):
        return re.search(
            r"/name/(?P<id>\w+)/",
            self.rows[index].get('href')
        ).group("id")

    def get_data_at(self, index):
        return [
            self.movie_id,
            self.get_id(index)
        ]

    def get_data(self):
        data = []
        index = 0
        while index < len(self.rows):
            data.append(self.get_data_at(index))
            index += 1
        return data


class MovieOpeningWeeked:
    def __init__(self, movie_id, soup):
        self.movie_id = movie_id
        details = soup.find("div", {"id": "title-overview-widget"})
        table = None
        if details:
            table = details.find("h4", text=re.compile(r"Director[s]{0,1}:"))
        if not table:
            self.rows = []
        else:
            self.rows = table.find_next_siblings("a", {'itemprop': 'url'})

    def get_id(self, index):
        return re.search(
            r"/name/(?P<id>\w+)/",
            self.rows[index].get('href')
        ).group("id")

    def get_data_at(self, index):
        return [
            self.movie_id,
            self.get_id(index)
        ]

    def get_data(self):
        data = []
        index = 0
        while index < len(self.rows):
            data.append(self.get_data_at(index))
            index += 1
        return data


class MovieWriter:
    def __init__(self, movie_id, soup):
        self.movie_id = movie_id
        details = soup.find("div", {"id": "title-overview-widget"})
        table = None
        if details:
            table = details.find("h4", text=re.compile(r"Writer[s]{0,1}:"))
        if not table:
            self.rows = []
        else:
            self.rows = table.find_next_siblings("a", {'itemprop': 'url'})

    def get_id(self, index):
        return re.search(
            r"/name/(?P<id>\w+)/",
            self.rows[index].get('href')
        ).group("id")

    def get_data_at(self, index):
        return [
            self.movie_id,
            self.get_id(index)
        ]

    def get_data(self):
        data = []
        index = 0
        while index < len(self.rows):
            data.append(self.get_data_at(index))
            index += 1
        return data


class MovieProduction:
    def __init__(self, movie_id, soup):
        self.movie_id = movie_id
        table = soup.find("h4", text="Production Co:")
        if not table:
            self.rows = []
        else:
            self.rows = table.find_next_siblings("span", {"itemprop": "creator"})

    def get_id(self, index):
        return re.search(
            r"/company/(?P<id>\w+)?",
            self.rows[index].find("a").get('href')
        ).group("id")

    def get_data_at(self, index):
        return [
            self.movie_id,
            self.get_id(index)
        ]

    def get_data(self):
        data = []
        index = 0
        while index < len(self.rows):
            data.append(self.get_data_at(index))
            index += 1
        return data


class MovieReleaseDate:
    def __init__(self, movie_id, soup):
        self.movie_id = movie_id
        table = soup.find("table", {"id": "release_dates"})
        if not table:
            self.rows = []
        else:
            self.rows = table.findAll("tr")

    def get_country(self, index):
        return self.rows[index].findAll("td")[0].get_text().strip().encode("utf-8")

    def get_date(self, index):
        return self.rows[index].findAll("td")[1].get_text().strip()

    def get_remarks(self, index):
        remarks = (self.rows[index]
                       .findAll('td')[2]
                       .get_text()
                       .encode("utf-8")
                       .strip()
                       .replace("\n", "")
                       .replace("\r", ""))
        remarks = re.sub(" {2,}", " ", remarks)
        if not remarks:
            return None
        return remarks

    def get_data_at(self, index):
        return [
            self.movie_id,
            self.get_country(index),
            self.get_date(index),
            self.get_remarks(index)
        ]

    def get_data(self):
        data = []
        index = 0
        while index < len(self.rows):
            data.append(self.get_data_at(index))
            index += 1
        return data


class MovieCast:
    def __init__(self, movie_id, soup):
        self.movie_id = movie_id
        table = soup.find("table", {"class": "cast_list"})
        if not table:
            self.rows = []
        else:
            self.rows = table.findAll("tr", {"class": ["odd", "even"]})

    def get_id(self, index):
        href = self.rows[index].findAll("td")[1].find('a').get('href')
        return re.search('/name/(?P<id>\w+)/', href).group('id')

    def get_character(self, index):
        character = (self.rows[index]
                        .findAll("td")[3]
                        .get_text()
                        .strip()
                        .encode('utf-8')
                        .replace("\n", "")
                        .replace("\r", ""))
        return re.sub(" {2,}", " ", character)

    def get_data_at(self, index):
        return [
            self.movie_id,
            self.get_id(index),
            self.get_character(index)
        ]

    def get_data(self):
        data = []
        index = 0
        while index < len(self.rows):
            data.append(self.get_data_at(index))
            index += 1
        return data


def get_total_page(year):
    url = SEARCH_URL % (0, year, year)
    soup = get_soup_page(url)
    if not soup:
        return 0
    _ = (soup.find("div", {"class": "leftright"})
             .find("div", {"id": "left"})
             .get_text()
             .strip())
    total_record = int(re.search(r"of (?P<total>[0-9,]+)\s*titles", _)
                         .group('total')
                         .replace(",", ""))
    return int(math.ceil(total_record / float(RECORD_PER_PAGE)))


def get_soup_page(url):
    # Always sleep before making any call
    time.sleep(2)
    try:
        print "[STATUS] Connecting to URL: %s." % url
        webpage = urlopen(url).read()
    except Exception, e:
        print "[ERROR] Can't connect to URL: %s. Reason: %s." % (url, e)
        sys.exit(1)
    else:
        print "[STATUS] Connected. Parsing URL content."
        return BeautifulSoup(webpage.decode('utf-8', "ignore"))


def run(year, from_page, to_page):

    output_m = os.path.join("results", year, "movie", OUTPUT_FILE)
    output_c = os.path.join("results", year, "cast", OUTPUT_FILE)
    output_r = os.path.join("results", year, "release", OUTPUT_FILE)
    output_d = os.path.join("results", year, "director", OUTPUT_FILE)
    output_w = os.path.join("results", year, "writer", OUTPUT_FILE)
    output_p = os.path.join("results", year, "production", OUTPUT_FILE)
    output_g = os.path.join("results", year, "genre", OUTPUT_FILE)

    create_folder(output_m)
    create_folder(output_c)
    create_folder(output_r)
    create_folder(output_d)
    create_folder(output_w)
    create_folder(output_p)
    create_folder(output_g)

    page_number = 0
    total = 0
    for page_number in range(from_page, to_page):
        start_at = 1 + page_number * RECORD_PER_PAGE
        url = SEARCH_URL % (start_at, year, year)
        soup = get_soup_page(url)

        rows = (soup.find("table", {"class": "results"})
                    .find_all('tr', {'class': ['even', 'odd']}))

        with open(output_m % ("movie", year, page_number), "w") as f_m, open(output_c % ("cast", year, page_number), "w") as f_c, open(output_r % ("release", year, page_number), "w") as f_r, open(output_d % ("director", year, page_number), "w") as f_d, open(output_w % ("writer", year, page_number), "w") as f_w, open(output_p % ("production", year, page_number), "w") as f_p, open(output_g % ("genre", year, page_number), "w") as f_g:

            writer_m = csv.writer(f_m, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
            writer_c = csv.writer(f_c, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
            writer_r = csv.writer(f_r, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
            writer_d = csv.writer(f_d, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
            writer_w = csv.writer(f_w, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
            writer_p = csv.writer(f_p, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
            writer_g = csv.writer(f_g, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)

            for row in rows:
                detail_url = (row.find("td", {"class": "title"})
                                 .find("a")
                                 .get("href"))
                detail_soup = get_soup_page(BASE_URL + detail_url)
                movie_id = (re.search(r"/title/(?P<movie_id>\w+)/",
                                     detail_url)
                              .group("movie_id"))

                movie = Movie(movie_id, detail_soup)
                print " - Parsed %s" % movie.get_title()
                writer_m.writerow(movie.get_data())

                genre = MovieGenre(movie_id, detail_soup)
                results = genre.get_data()
                print "   + Parsed %d genres" % len(results)
                writer_g.writerows(results)

                director = MovieDirector(movie_id, detail_soup)
                results = director.get_data()
                print "   + Parsed %d directors" % len(results)
                writer_d.writerows(results)

                writer = MovieWriter(movie_id, detail_soup)
                results = writer.get_data()
                print "   + Parsed %d writers" % len(results)
                writer_w.writerows(results)

                production = MovieWriter(movie_id, detail_soup)
                results = production.get_data()
                print "   + Parsed %d productions" % len(results)
                writer_p.writerows(results)

                cast = MovieCast(movie_id, detail_soup)
                results = cast.get_data()
                print "   + Parsed %d casts" % len(results)
                writer_c.writerows(results)

                release_url = detail_soup.find("a", text="Release Dates")
                if release_url:
                    release_date = MovieReleaseDate(
                        movie_id, get_soup_page(BASE_URL + release_url.get('href'))
                    )
                    results = release_date.get_data()
                    print "   + Parsed %d release dates" % len(results)
                    writer_r.writerows(results)

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
    for year in ["2013"]:
        print "[STATUS] Counting total page for %s" % year
        total_page = get_total_page(year)
        print "[STATUS] Found %s pages" % total_page
        #run(year, 0, total_page)
        run(year, 70, 90)
        print "[STATUS] Long sleeping ......"
        time.sleep(30)
