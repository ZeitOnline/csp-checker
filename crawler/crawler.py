import requests
import lxml.etree
import selenium.webdriver
import os
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import logging
import argparse


log = logging.getLogger('csp_crawler')

NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
SITEMAP_URL = 'http://www.zeit.de/gsitemaps/index.xml'
REPLACE_URL = ('http://www.zeit.de', 'https://test-ssl.zeit.de')
IGNORE_PATTERN = []


def get_urls(sitemaps):
    for sitemap_url in sitemaps:
        sitemap = get_sitemap(sitemap_url)
        for url in sitemap:
            yield url.find('{%s}loc' % NS).text


def get_sitemap(sitemap_url):
    return lxml.etree.fromstring(requests.get(sitemap_url).content)


def browser():
    opts = Options()
    opts.add_argument('headless')
    opts.add_argument('disable-gpu')
    opts.add_argument('window-size=1200x800')
    opts.binary_location = os.environ.get('ZEIT_WEB_CHROMIUM_BINARY')
    parameters = {'chrome_options': opts}
    return selenium.webdriver.Chrome(**parameters)


def browse_article(url):
    global BROWSER
    try:
        return BROWSER.get(url)
    except WebDriverException:
        try:
            log.warn("Needed to reinstatiate browser")
            BROWSER = browser()
            return BROWSER.get(url)
        except Exception:
            log.warn("Could not browse {}", url)


def crawl_sitemap(sitemap, orig_uri, replace_uri, ignore_pattern):
    req = requests.get(sitemap)
    xml = lxml.etree.fromstring(req.content)
    sitemaps = [elem[0].text.strip() for elem in xml]

    log.info("Start crawling URLS from: {}".format(sitemap))
    for url in get_urls(sitemaps):
        process_url(url, orig_uri, replace_uri, ignore_pattern)


def crawl_file(path, orig_uri, replace_uri, ignore_pattern):
    with open(path) as f:
        for line in f.readlines():
            url = line.strip("\\n")
            process_url(url, orig_uri, replace_uri, ignore_pattern)


def process_url(url, orig_uri, replace_uri, ignore_pattern):
        url = url.replace(orig_uri, replace_uri)
        if any(x in url for x in ignore_pattern):
            return
        browse_article(url)
        log.info(url)


BROWSER = browser()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=('Get all URLs in a sitemap and process them '
                     'with a headless browser.'))

    parser.add_argument(
        '--sitemap',
        dest='sitemap',
        default=SITEMAP_URL,
        help='The URL of the sitemap to crawl.')
    parser.add_argument(
        '--orig-uri',
        dest='orig_uri',
        default=REPLACE_URL[0],
        help='The original URI as stated in the sitemap.')

    parser.add_argument(
        '--replace-uri',
        dest='replace_uri',
        default=REPLACE_URL[1],
        help='The URI to replace orig-uri with')

    parser.add_argument(
        '--ignore-pattern',
        dest='ignore_pattern',
        action='append',
        default=IGNORE_PATTERN,
        help='One or more patterns in URIs, which are not to browse')

    parser.add_argument(
        '--log-file',
        dest='log_file',
        default='crawler.log',
        help='Where to store the logfile for a crawl.')

    parser.add_argument(
        '--log-format',
        dest='log_format',
        default='%(asctime)s %(levelname)s %(message)s',
        help='Format of the log entries.')

    parser.add_argument(
        '--mode',
        dest='mode',
        default='sitemap',
        help='Crawl sitemap or list of URLs (pass location)')

    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format=args.log_format,
        datefmt='%Y-%m-%d %H:%M:%S')

    if args.mode == 'sitemap':
        crawl_sitemap(args.sitemap, args.orig_uri, args.replace_uri,
                      args.ignore_pattern)
    else:
        crawl_file(args.mode, args.orig_uri, args.replace_uri,
                   args.ignore_pattern)
