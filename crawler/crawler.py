import requests
import lxml.etree
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
import os
import argparse


log = logging.getLogger('csp_crawler')

NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
SITEMAP_URL = os.environ.get('SITEMAP_URL', None)
REPLACE_URL = ('http://www.zeit.de', 'https://test-ssl.zeit.de')
IGNORE_PATTERN = []
REMOTE_SELENIUM = os.environ.get('REMOTE_SELENIUM', 'http://127.0.0.1:4444')


def get_urls(sitemaps):
    for sitemap_url in sitemaps:
        sitemap = get_sitemap(sitemap_url)
        for url in sitemap:
            yield url.find('{%s}loc' % NS).text


def get_sitemap(sitemap_url):
    return lxml.etree.fromstring(requests.get(sitemap_url).content)


def browser():
    return webdriver.Remote(
        command_executor='{}/wd/hub'.format(REMOTE_SELENIUM),
        desired_capabilities=DesiredCapabilities.CHROME)


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


def crawl_sitemap(sitemap, orig_uri, replace_uri,
                  ignore_pattern, continue_with, stop_at):
    req = requests.get(sitemap)
    xml = lxml.etree.fromstring(req.content)
    sitemaps = [elem[0].text.strip() for elem in xml]

    log.info("Start crawling URLS from: {}".format(sitemap))
    for url in get_urls(sitemaps):
        if url == stop_at:
            log.info("Stop processing at {}".format(url))
            return
        if continue_with is None or continue_with == url:
            process_url(url, orig_uri, replace_uri, ignore_pattern)
            continue_with = None
        else:
            log.info("Skip {}".format(url))


def crawl_file(path, orig_uri, replace_uri, ignore_pattern, continue_with,
               stop_at):
    with open(path) as f:
        for line in f.readlines():
            url = line.strip("\\n")
            if url == stop_at:
                log.info("Stop processing at {}".format(url))
                return
            if continue_with is None or continue_with == url:
                process_url(url, orig_uri, replace_uri, ignore_pattern)
                continue_with = None
            else:
                log.info("Skip {}".format(url))


def process_url(url, orig_uri, replace_uri, ignore_pattern):
        url = url.replace(orig_uri, replace_uri)
        if any(x in url for x in ignore_pattern):
            return
        browse_article(url)
        log.info(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            'Get all URLs in a sitemap and process them'
            ' with a headless browser.\n\n'
            'Environment variables set to:\n'
            'SITEMAP_URL: {}\n'
            'REMOTE_SELENIUM: {}'.format(SITEMAP_URL, REMOTE_SELENIUM)),
        formatter_class=argparse.RawTextHelpFormatter)

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
        help='Crawl sitemap or list of URLs (pass location).')

    parser.add_argument(
        '--continue-with',
        dest='continue_with',
        default=None,
        help='Skip urls in sitemap or list before this url.')

    parser.add_argument(
        '--stop-at',
        dest='stop_at',
        default=None,
        help='Process urls until your reach this url in sitemap or list.')

    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format=args.log_format,
        datefmt='%Y-%m-%d %H:%M:%S')

    global BROWSER
    BROWSER = browser()
    crawl = crawl_sitemap
    if not args.mode == 'sitemap':
        crawl = crawl_file
    crawl(args.sitemap, args.orig_uri, args.replace_uri,
          args.ignore_pattern, args.continue_with, args.stop_at)
