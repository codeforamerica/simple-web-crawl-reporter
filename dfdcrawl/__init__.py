import logging

logging.basicConfig(format='%(levelname)10s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_debug = lambda *args: logger.debug(' '.join(map(str, args)))

from urlparse import urljoin, urlsplit, urlunsplit
from time import time

from bs4 import BeautifulSoup
from requests.exceptions import TooManyRedirects
from requests import get, head

UA_STRING = 'Code for America Simple Web Crawler <https://github.com/codeforamerica/simple-web-crawl-reporter>'

def nice_time(time):
    if time <= 90:
        return '{:.0f} seconds'.format(time)
    if time < 60 * 60 * 1.5:
        return '{:.0f} minutes'.format(time / 60)
    if time < 24 * 60 * 60 * 1.5:
        return '{:.0f} hours'.format(time / 3600)
    if time < 7 * 24 * 60 * 60 * 1.5:
        return '{:.0f} days'.format(time / 86400)
    if time < 30 * 24 * 60 * 60 * 1.5:
        return '{:.0f} weeks'.format(time / 604800)

    return '{:.0f} months'.format(time / 2592000)

def get_soup_ingredients(html):
    ''' Return HTML title and list of hrefs for HTML data.
    '''
    head = html[html.index('<head'):html.index('</head')]
    body = html[html.index('<body'):html.index('</body')]
    
    title = BeautifulSoup(head).find('title').text
    hrefs = [a.get('href', '') for a in BeautifulSoup(body).find_all('a')]
    
    return title, hrefs

def crawl(start_url, hostname_regexps, ignore_regexps, parsed, problems, limit):
    '''
    '''
    for host in hostname_regexps:
        logger.debug('"{}" is an acceptable hostname pattern'.format(host.pattern))
    
    for ignore in ignore_regexps:
        logger.debug('"{}" is a URL to ignore'.format(ignore.pattern))
    
    start_time = time()
    request_kwargs = dict(allow_redirects=True, headers={'User-Agent': UA_STRING})

    urls = [(start_url, None, 0)]
    seen = set()

    while urls:
        # Stop if a limit was given.
        if limit and len(seen) >= limit:
            logger.info('Stopping after {} URLs'.format(limit))
            break
    
        url, referer, hops = urls.pop(0)
        urls = filter(lambda (u, r, h): u != url, urls)

        if url in seen:
            log_debug(len(urls), 'seen', url)
            continue
    
        try:
            got = head(url, **request_kwargs)
        except Exception as e:
            logger.warning('Error in HEAD request for {}: {}'.format(url, e))
            continue
    
        if got.url in seen:
            log_debug(len(urls), 'seen', got.url)
            continue
    
        seen.add(url)
        seen.add(got.url)

        # The URL might need to be ignored.
        ignore_matches = [True for pat in ignore_regexps if pat.match(got.url)]

        if ignore_matches:
            log_debug(len(urls), 'ignoring', got.url)
            continue
    
        # The URL might be one some other host.
        host = urlsplit(got.url).netloc
        host_matches = [True for pat in hostname_regexps if pat.match(host)]

        if not host_matches:
            logger.debug('Skipping {}'.format(got.url))
            continue
    
        if got.status_code != 200:
            problems.writerow((got.status_code, url, referer))
            logger.warning('Got HTTP status {} for {}'.format(got.status_code, got.url))
            continue
    
        if 'content-type' in got.headers:
            if not got.headers['content-type'].startswith('text/html'):
                log_debug(len(urls), 'skipping', got.url)
                continue
    
        seconds_remain = (time() - start_time) * len(urls) / len(seen)
        logger.info('{} est. {} left with {:,d} URLs to go'.format(got.url, nice_time(seconds_remain), len(urls)))
    
        start = time()
        got = get(url, **request_kwargs)
        elapsed = time() - start

        try:
            title, hrefs = get_soup_ingredients(got.content)
        except Exception as e:
            logger.warning('Failed to parse HTML from {}: {}'.format(got.url, e))
            title, hrefs = u'', []
        finally:
            parsed.writerow((got.url.encode('utf8'), title.encode('utf8'), round(elapsed, 3), hops))
    
        for href in set(hrefs):
            link = urljoin(got.url, href)
            scheme, host, path, query, _ = urlsplit(link)
            link = urlunsplit((scheme, host, path, query, ''))
        
            if href in ('#', ''):
                problems.writerow(('Empty', href.encode('utf8'), got.url.encode('utf8')))
        
            elif href.startswith('#'):
                # ignore internal anchors
                continue
        
            elif path.endswith('.pdf'):
                # skip PDF downloads
                continue
        
            elif link not in seen:
                urls.append((link, got.url, hops+1))
