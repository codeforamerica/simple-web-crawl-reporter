from bs4 import BeautifulSoup
from requests.exceptions import TooManyRedirects
from requests import get, head

from csv import writer
from urlparse import urljoin, urlsplit, urlunsplit
from re import compile

ignore = compile(r'/blog/')
ignore = compile(r'/00000')

base_url = 'http://localhost/~migurski/Codeforamerica.org'
base_url = 'http://alpha.codeforamerica.org'
base_url = 'http://www2.oaklandnet.com'
urls = [(base_url, None, 0)]
seen = set()

parsed = writer(open('parsed-links-oaklandnet.csv', 'w'))
parsed.writerow(('URL', 'Clicks'))

problems = writer(open('checked-links-oaklandnet.csv', 'w'))
problems.writerow(('Problem', 'URL', 'Referer'))

while urls: # and len(seen) < 20:
    url, referer, hops = urls.pop(0)
    
    if url in seen:
        print len(urls), 'seen', url
        continue
    
    try:
        got = head(url, allow_redirects=True)
    except TooManyRedirects:
        print '!!!', url
        raise
    
    if got.url in seen:
        print len(urls), 'seen', got.url
        continue
    
    seen.add(url)
    seen.add(got.url)

    if ignore.match(got.url[len(base_url):]):
        print len(urls), 'ignoring', got.url
        continue
    
    if not got.url.startswith(base_url):
        print len(urls), 'skipping', got.url
        continue
    
    if got.status_code != 200:
        problems.writerow((got.status_code, url, referer))
        continue
    
    if not got.headers['content-type'].startswith('text/html'):
        print len(urls), 'skipping', got.url
        continue
    
    print len(urls), got.url
    parsed.writerow((got.url, hops))
    
    data = get(url, allow_redirects=True).content
    body = data[data.index('<body'):data.index('</body')]
    soup = BeautifulSoup(body)
    hrefs = [a.get('href', '') for a in soup.find_all('a')]
    
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
