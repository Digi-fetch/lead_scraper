# -*- coding: utf-8 -*-
from lxml import html
import requests
import sqlite3


class Spider(object):
    """All other crawler classes will inherit from this one to reduce code"""
    def __init__(self, searchterm, city, province):
        self.searchterm = searchterm
        self.city = city
        self.province = province


class Indeed(object):
    """indeed.ca scraper. Takes in url parameter including search terms and location that
    will be fed into the url"""

    def __init__(self, searchterm, city, province):
        self.searchterm = searchterm
        self.city = city
        self.province = province

    def crawl(self):
        count = 0
        while True:
            searchterm = self.searchterm
            city = self.city
            prov = self.province
            url = "http://ca.indeed.com/jobs?q="+searchterm+'&l='+city+"%2C+"+prov+'&start='+str(count)
            page = requests.get(url)
            tree = html.fromstring(page.text)
            jobtitles = tree.xpath('//h2[@class="jobtitle"]/a/text()')
            print jobtitles
            # used to cycle through pages i.e: 10=page2 20=page3 etc...
            count += 10
            # jobtitles is too large of a list so I need to find a way to add 1 job at a time
            Database.add_entry(jobtitles[0][0]) # comment out this line if you want to test the scraper without getting errors
            # ad logic to check if page is the same as the precedent page
            # so I stop stop scraping once I hit the last page


class Database(object):
    """jobsite paremeter is name of the job website. there will be 1 db for each job website"""
    def __init__(self, jobsite):
        # unused for now
        db = sqlite3.connect(jobsite+'.db')
        c = db.cursor()

    @staticmethod
    def add_entry(jobtitles):
        conn = sqlite3.connect('jobs.db')
        c = conn.cursor()

        # Create table if needed
        table = 'CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, jobtitles TEXT)'
        c.execute(table)

        # Insert all data entry
        c.execute('''INSERT INTO jobs (jobtitles)
        VALUES (?)''', (jobtitles))

        conn.commit()
        c.close()


def main():
    test = Indeed('it', 'toronto', 'ON')
    test.crawl()


if __name__ == '__main__':
    main()