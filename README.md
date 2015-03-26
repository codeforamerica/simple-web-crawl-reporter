Simple Web Crawl Reporter
=========================

This _work-in-progress_ site crawling tool can be used to audit a website and
output a list of pages in CSV format. Code for America has developed this tool
[as parts of its Digital Front Door initiative](http://www.codeforamerica.org/our-work/initiatives/digitalfrontdoor/).

Use
---

Run the crawler on the command line:

    link-check-oaklandnet.py <site URL> <output CSV filename>

More options:

    link-check-oaklandnet.py --help

Install
-------

The crawler is written in [Python](https://github.com/codeforamerica/howto/blob/master/Python-Virtualenv.md)
and requires [Requests](http://docs.python-requests.org/en/latest/) and
[Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/) for use.
Crawling is single-threaded.
