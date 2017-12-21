import requests
import lxml.etree
import selenium.webdriver
import os
from selenium.webdriver.chrome.options import Options

NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'


def get_article_urls(sitemaps):
    for sitemap_url in sitemaps:
        sitemap = get_sitemap(sitemap_url)
        for url in sitemap:
            yield url.find('{%s}loc' % NS).text


def get_sitemap(sitemap_url):
    return lxml.etree.fromstring(requests.get(sitemap_url).content)


def browser():
    opts = Options()

    # opts.add_argument('headless')
    opts.add_argument('disable-gpu')
    opts.add_argument('window-size=1200x800')
    opts.binary_location = os.environ.get('ZEIT_WEB_CHROMIUM_BINARY')
    parameters = {'chrome_options': opts}
    return selenium.webdriver.Chrome(**parameters)


def browse_article(article_url):
    return BROWSER.get(article_url)


BROWSER = browser()

if __name__ == "__main__":
    req = requests.get("http://www.zeit.de/gsitemaps/index.xml")
    xml = lxml.etree.fromstring(req.content)
    sitemaps = [elem[0].text.strip() for elem in xml]
    print ("Start crawling: ")
    for article_url in get_article_urls(sitemaps):
        article_url = article_url.replace(
            'http://www.zeit.de',
            'https://test-ssl.zeit.de')
        article = browse_article(article_url)
        print(article_url)
        print("------------------------")
