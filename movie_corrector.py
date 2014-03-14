# -*- coding: iso-8859-15 -*-

import csv
import pprint
import re

INPUT_FILE = "movie_2013.csv"
OUTPUT_FILE = "movie_2013_fixed.csv"
OUTPUT_CURRENCY_FILE = "currency.csv"

unique_currencies = {}


class Movie:
    BUDGET = 5
    OPENING_WEEKEND_GROSS = 6
    LATEST_GROSS = 9

    def __init__(self, data):
        self.data = data
        self.currency_codes = (
            ('$', 'USD'),
            (u"£", 'GBP'),
            (u"€", 'EUR')
        )

    def get_currency(self, val):
        val = val.strip()
        if not val:
            return None

        currency = re.search(r'(?P<currency>[^0-9,.]+)', val).group('currency').strip()

        if len(currency) > 3:
            currency = currency[0:3]

        elif len(currency) <= 3:
            for (symbol, code) in self.currency_codes:
                if symbol.encode("utf-8") == str(currency):
                    currency = code
                    break

        unique_currencies.setdefault(currency, 0)
        unique_currencies[currency] += 1

        return currency

    def get_nominal(self, val):
        val = val.strip()
        if not val:
            return None

        nominal = re.search('(?P<nominal>[0-9,.]+)', val).group('nominal')
        return int(nominal.replace(",", ""))

    def get_budget_currency(self):
        return self.get_currency(self.data[self.BUDGET])

    def get_budget_nominal(self):
        return self.get_nominal(self.data[self.BUDGET])

    def get_opening_weekend_gross_currency(self):
        return self.get_currency(self.data[self.OPENING_WEEKEND_GROSS])

    def get_opening_weekend_gross_nominal(self):
        return self.get_nominal(self.data[self.OPENING_WEEKEND_GROSS])

    def get_latest_gross_currency(self):
        return self.get_currency(self.data[self.LATEST_GROSS])

    def get_latest_gross_nominal(self):
        return self.get_nominal(self.data[self.LATEST_GROSS])

    def get_new_format(self):
        new_data = self.data[:]
        # Caution, sequence REALLY matters!!!
        # Do it in reverse, start from the last
        new_data.insert(self.LATEST_GROSS + 1,
                        self.get_latest_gross_nominal())
        new_data[self.LATEST_GROSS] = self.get_latest_gross_currency()

        new_data.insert(self.OPENING_WEEKEND_GROSS + 1,
                        self.get_opening_weekend_gross_nominal())
        new_data[self.OPENING_WEEKEND_GROSS] = self.get_latest_gross_currency()

        new_data.insert(self.BUDGET + 1, self.get_budget_nominal(), )
        new_data[self.BUDGET] = self.get_budget_currency()

        return new_data


def run(input_file, output_file, currency_file):
    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        writer = csv.writer(f_out, delimiter=';', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        reader = csv.reader(f_in, delimiter=';', quotechar='"')
        total = 0
        for row in reader:
            movie = Movie(row)
            writer.writerow(movie.get_new_format())
            total += 1

    print "[STATUS] Parsing %s records done" % total

    pprint.pprint(unique_currencies)
    with open(currency_file, "w") as f_out:
        writer = csv.writer(f_out, delimiter=';', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        keys = unique_currencies.keys()
        keys.sort()
        for k in keys:
            writer.writerow([k])
    print "[STATUS] Writing unique currencies done"

if __name__ == "__main__":
    run(INPUT_FILE, OUTPUT_FILE, OUTPUT_CURRENCY_FILE)
