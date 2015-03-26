from __future__ import division

from dfdcrawl import crawl

from csv import writer
from urlparse import urlsplit
from argparse import ArgumentParser
from re import compile, IGNORECASE

parser = ArgumentParser(description='Yo')

parser.add_argument('url', help='Starting URL.')
parser.add_argument('output', help='Output CSV filename.')

parser.add_argument('-i', '--ignore', action='append', default=[],
                    help='Add a URL regular expression to ignore.')

parser.add_argument('-a', '--accept', action='append', default=[],
                    help='Add an acceptable hostname beyond the starting URL.')

parser.add_argument('-e', '--errors', default='/dev/null',
                    help='Error CSV filename.')

if __name__ == '__main__':
    args = parser.parse_args()
    
    start_url = args.url
    
    output = writer(open(args.output, 'w', buffering=1))
    output.writerow(('URL', 'Title', 'Load Time', 'Clicks Deep'))
    
    errors = writer(open(args.errors, 'w', buffering=1))
    errors.writerow(('Problem', 'URL', 'Referer'))

    ignore_regexps = [compile(pattern, IGNORECASE) for pattern in args.ignore]
    host_patterns = [urlsplit(start_url).netloc.replace('.', '\.')] + args.accept
    host_regexps = [compile(pattern, IGNORECASE) for pattern in host_patterns]
    
    crawl(start_url, host_regexps, ignore_regexps, output, errors)
