import logging

logging.basicConfig(format='%(levelname)10s %(message)s')
logger = logging.getLogger('link-check')
logger.setLevel(logging.DEBUG)

log_critical = lambda *args: logger.critical(' '.join(map(str, args)))
log_debug = lambda *args: logger.debug(' '.join(map(str, args)))
log_info = lambda *args: logger.info(' '.join(map(str, args)))

from bs4 import BeautifulSoup
from requests.exceptions import TooManyRedirects
from requests import get, head

from csv import writer
from urlparse import urljoin, urlsplit, urlunsplit
from re import compile
from time import time

ignore = compile(r'/blog/')
ignore = compile(r'/00000')

base_url = 'http://localhost/~migurski/Codeforamerica.org'
base_url = 'http://alpha.codeforamerica.org'
base_url = 'http://www2.oaklandnet.com'
base_url = 'http://www.cstx.gov'
urls = [(base_url, None, 0)]
seen = set()

parsed = writer(open('parsed-links-oaklandnet.csv', 'w', buffering=1))
parsed.writerow(('URL', 'Title', 'Load Time', 'Clicks Deep'))

problems = writer(open('checked-links-oaklandnet.csv', 'w', buffering=1))
problems.writerow(('Problem', 'URL', 'Referer'))

def get_soup_ingredients(html):
    ''' Return HTML title and list of hrefs for HTML data.
    '''
    head = html[html.index('<head'):html.index('</head')]
    body = html[html.index('<body'):html.index('</body')]
    
    title = BeautifulSoup(head).find('title').text
    hrefs = [a.get('href', '') for a in BeautifulSoup(body).find_all('a')]
    
    return title, hrefs

while urls: # and len(seen) < 20:
    url, referer, hops = urls.pop(0)
    
    if url in seen:
        log_debug(len(urls), 'seen', url)
        continue
    
    try:
        got = head(url, allow_redirects=True)
    except TooManyRedirects:
        log_critical('!!!', url)
        raise
    
    if got.url in seen:
        log_debug(len(urls), 'seen', got.url)
        continue
    
    seen.add(url)
    seen.add(got.url)

    # The URL might need to be ignored.
    if ignore.match(got.url[len(base_url):]):
        log_debug(len(urls), 'ignoring', got.url)
        continue
    
    # The URL might be one some other host.
    if not got.url.startswith(base_url):
        log_debug(len(urls), 'skipping', got.url)
        continue
    
    if got.status_code != 200:
        problems.writerow((got.status_code, url, referer))
        continue
    
    if not got.headers['content-type'].startswith('text/html'):
        log_debug(len(urls), 'skipping', got.url)
        continue
    
    log_info(len(urls), got.url)
    
    start = time()
    got = get(url, allow_redirects=True)
    elapsed = time() - start

    title, hrefs = get_soup_ingredients(got.content)
    parsed.writerow((got.url, title, round(elapsed, 3), hops))
    
    for href in set(hrefs):
        link = urljoin(got.url, href)
        scheme, host, path, query, _ = urlsplit(link)
        link = urlunsplit((scheme, host, path, query, ''))
        
        if href in ('#', ''):
            problems.writerow(('Empty', href, got.url))
        
        elif href.startswith('#'):
            # ignore internal anchors
            continue
        
        elif not link.startswith(base_url):
            # ignore external links
            continue
        
        elif path.endswith('.pdf'):
            # skip PDF downloads
            continue
        
        elif link not in seen:
            urls.append((link, got.url, hops+1))
