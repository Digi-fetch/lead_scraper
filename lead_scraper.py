# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from lxml import html
import requests
import sqlite3
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import time



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
        # count starts at first page
        crawling = True
        count = 970
        time.sleep(1)
        while crawling:
            searchterm = self.searchterm
            city = self.city
            prov = self.province
            url = "http://ca.indeed.com/jobs?q="+searchterm+'&l='+city+"%2C+"+prov+'&start='+str(count)
            print(url, 'current URL')
            page = requests.get(url)
            tree = html.fromstring(page.text)
            jobtitles = tree.xpath('//h2[@class="jobtitle"]/a/text()')
            joblinks = tree.xpath('//h2[@class="jobtitle"]/a/@href')
            job_descriptions = tree.xpath('//span[@class="summary"]/text()')
            jobtitles = (job.lstrip() for job in jobtitles)
            joblinks = (job.lstrip() for job in joblinks)
            job_descriptions = (job.lstrip() for job in job_descriptions)
            Database.add_entry(zip(jobtitles, joblinks, job_descriptions))
            link_pages = tree.xpath('//div[@class="pagination"]/a/@href')
            print(link_pages, 'link_pages')
            # look for next button
            # if no longer present it means we have reached the last page
            next_button = tree.xpath('//*[@id="resultsCol"]/div/a/span/span/text()')
            next_button_str = ''.join(next_button)
            print(next_button)

            if u'Next' in next_button_str:
                print('found next will continue scraping...')
            else:
                print('Hit last page, crawler will stop...')
                crawling = False

            for page in link_pages:
                # takes digits from end of url
                # takes last 6 characters, unlikely that the number would be any bigger
                p = page[-6:]
                digits_url = ''.join([d for d in p if d.isdigit()])
                try:
                    print(digits_url, 'digits url')
                    if digits_url > count:
                        print(page, 'page')
                        count = int(digits_url)
                        print(count, 'count')
                    else:
                        print('You probably broke your conditional statement...')
                        print(digits_url, 'current count {}'.format(count))
                except ValueError:
                    # print("We're on the first page so no int in the page url")
                    print('This failed', digits_url)


class Database(object):
    @staticmethod
    def add_entry(job_offers):
        conn = sqlite3.connect('jobs.db')
        with conn:
            c = conn.cursor()
            # Create table if needed
            table = 'CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, job_titles TEXT, job_links TEXT, job_descriptions TEXT)'
            c.execute(table)
            # Insert all data entry
            c.executemany('''INSERT INTO jobs (job_titles, job_links, job_descriptions) VALUES (?,?,?)''', job_offers)

    @staticmethod
    def filter_jobs(search_term):
        """searches the sql db for a job keyword.
        Prints out the entire row for each match
        """
        conn = sqlite3.connect('jobs.db')
        with conn:
            c = conn.cursor()
            c.execute('''SELECT * FROM jobs''')
            search_title = [row for row in c if search_term.lower() in row[1].lower()]
            # Need another c.execute otherwise I can't access the db a second time
            c.execute('''SELECT * FROM jobs''')
            search_desc = [col for col in c if search_term.lower() in col[3].lower()]
            search_terms = [search_title, search_desc]
            # print search_desc, 'DESC'
            # print search_title, 'TITLE'
            # Removes doubles. there can be doubles if keywords match both job_title and job_desc for the same job
            search_terms = set(tuple(i) for i in search_terms)

            try:
                print(search_terms)
                return search_terms
            except IndexError:
                print('Search term is most likely not in the database.' \
                      '\nTry scraping for the search term before running send_mail module.')


def send_mail(recipient, jobs):
    """Email module works as long as I don't use yahoo. gmail works as an alternative"""
    str_jobs = ''
    for c in str(jobs):
        str_jobs += c
    str_jobs = str_jobs.encode('utf-8')

    To = recipient
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Job found matching {} description.'
    msg['From'] = sender
    msg['To'] = recipient
    body = MIMEText(str_jobs, 'plain', 'UTF-8')
    msg.attach(body)

    # yahoo is the problem use google or another smtp provider
    # server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
    server = smtplib.SMTP('smtp-mail.outlook.com', 25)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender, password)
    print('sending mail..')
    server.sendmail(sender, [To], msg.as_string())
    print('mail sent')
    server.quit()
    # print 'done sending mail...'


def main():
    """Run test object first to scrape and populatre SQL DB
    then run Database.filter_jobs to find what you're looking for"""
    test = Indeed('it', 'Vancouver', 'BC')
    test.crawl()
    # search_terms = Database.filter_jobs('trainsim')
    # search_terms = Database.filter_jobs
    # send_mail('recipient@email.com', search_terms('manager'))


if __name__ == '__main__':
    main()