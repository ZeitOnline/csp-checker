import requests
import lxml.etree
import selenium.webdriver
import os
from selenium.webdriver.chrome.options import Options
import logging
import argparse


log = logging.getLogger('csp_crawler')

NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
SITEMAP_URL = 'http://www.zeit.de/gsitemaps/index.xml'
REPLACE_URL = ('http://www.zeit.de', 'https://test-ssl.zeit.de')
IGNORE_PATTERN = []


def get_article_urls(sitemaps):
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


def browse_article(article_url):
    return BROWSER.get(article_url)


BROWSER = browser()

if __name__ == "__main__":
    logging.basicConfig(
        filename='log/crawler.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    req = requests.get(SITEMAP_URL)
    xml = lxml.etree.fromstring(req.content)
    sitemaps = [elem[0].text.strip() for elem in xml]

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

    args = parser.parse_args()

    log.info("Start crawling URLS from: {}".format(SITEMAP_URL))
    for article_url in get_article_urls(sitemaps):
        article_url = article_url.replace(
            args.orig_uri,
            args.replace_uri)
        if any(x in article_url for x in args.ignore_pattern):
            continue
        article = browse_article(article_url)
        log.info(article_url)
