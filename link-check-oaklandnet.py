from __future__ import division

from dfdcrawl import crawl

from csv import writer
from urlparse import urlsplit
from re import compile

ignore = compile(r'/blog/')
ignore = compile(r'/00000')

base_url = 'http://localhost/~migurski/Codeforamerica.org'
base_url = 'http://alpha.codeforamerica.org'
base_url = 'http://www2.oaklandnet.com'
base_url = 'http://www.cstx.gov'

parsed = writer(open('parsed-links-oaklandnet.csv', 'w', buffering=1))
parsed.writerow(('URL', 'Title', 'Load Time', 'Clicks Deep'))

problems = writer(open('checked-links-oaklandnet.csv', 'w', buffering=1))
problems.writerow(('Problem', 'URL', 'Referer'))

crawl(base_url, [ignore], parsed, problems)
