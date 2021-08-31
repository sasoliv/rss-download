import re
import urllib.request
from urllib.request import urlopen
from xml.etree import ElementTree


class Feed:
    def __init__(self, regex, url):
        self.regex = regex
        self.url = url


def download(url):
    split = url.split("/")
    urllib.request.urlretrieve(url, "/home/ctw00452/Desktop/" + split[len(split) - 1])


def process_item(feed, item):
    title = list(filter(lambda child: child.tag == "title", list(item)))
    link = list(filter(lambda child: child.tag == "link", list(item)))
    if title.__sizeof__() <= 0 | link.__sizeof__() <= 0:
        return

    if re.match(feed.regex, title[0].text):
        download(link[0].text)


def process(feed):
    response = urlopen(feed.url)
    html_response = response.read()
    encoding = response.headers.get_content_charset('utf-8')
    decoded_html = html_response.decode(encoding)

    root = ElementTree.fromstring(decoded_html)
    channel = list(root)[0]
    items = filter(lambda item: item.tag == "item", list(channel))
    for item in items:
        process_item(feed, item)


def main():
    feeds = [
        Feed("^.*$", "https://nyaa.si/?page=rss&q=%5BSubsPlease%5D+Boruto+-+Naruto+Next+Generations+1080p&c=1_2&f=0")
    ]
    for feed in feeds:
        process(feed)


if __name__ == "__main__":
    main()
