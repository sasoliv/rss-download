import json
import re
import os
import urllib.request

from urllib.request import urlopen
from xml.etree import ElementTree


def overwrite(file, content):
    f = open(file, "w")
    f.write(content)
    f.close()


def read(file):
    f = open(file, "r")
    content = f.read()
    f.close()
    return content


def download(url, destination):
    split = url.split("/")
    filename = split[len(split) - 1]
    urllib.request.urlretrieve(url, destination + filename)
    print(url)


def process_item(feed, title, link):
    if title.__sizeof__() <= 0 | link.__sizeof__() <= 0:
        return

    if re.match(feed["regex"], title):
        download(link, os.path.expanduser(feed["destination"]))


def httpGet(url):
    response = urlopen(url)
    html_response = response.read()
    encoding = response.headers.get_content_charset('utf-8')
    return html_response.decode(encoding)


def doProcess(cacheFile, feed):
    response = httpGet(feed["url"])
    lastItem = read(cacheFile)

    root = ElementTree.fromstring(response)
    channel = list(root)[0]
    items = filter(lambda item: item.tag == "item", list(channel))
    for item in items:
        title = list(filter(lambda child: child.tag ==
                            "title", list(item)))[0].text
        link = list(filter(lambda child: child.tag ==
                           "link", list(item)))[0].text
        if title == lastItem:
            break

        process_item(feed, title, link)

    refreshCache(cacheFile, response)


def refreshCache(cacheFile, feedResponse):
    root = ElementTree.fromstring(feedResponse)
    channel = list(root)[0]
    items = filter(lambda item: item.tag == "item", list(channel))
    title = list(filter(lambda child: child.tag == "title", next(items)))
    overwrite(cacheFile, title[0].text)


def process(cacheFolder, feed):
    cacheFile = cacheFolder + "/" + feed["id"]
    if os.path.exists(cacheFile):
        doProcess(cacheFile, feed)
    else:
        refreshCache(cacheFile, httpGet(feed["url"]))


def main():
    home = os.path.expanduser("~")
    configFile = home + "/Desktop/rss-download/config.json"
    cacheFolder = home + "/.cache/rss-download"

    if not os.path.exists(cacheFolder):
        os.makedirs(cacheFolder)

    config = json.load(open(configFile))

    for feed in list(config["feeds"]):
        process(cacheFolder, feed)


if __name__ == "__main__":
    main()
