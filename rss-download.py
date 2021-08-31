import json
import re
import os
import time
import urllib.request

from datetime import datetime
from urllib.request import urlopen
from xml.etree import ElementTree


def nowStr():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def printNow(*values):
    print(nowStr(), *values)


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
    printNow("Starting download:", url)
    split = url.split("/")
    filename = split[len(split) - 1]
    finalFile = destination + "/" + filename
    urllib.request.urlretrieve(url, finalFile)
    printNow("Download done. Stored in:", finalFile)


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
    lastItem = read(cacheFile).strip()

    root = ElementTree.fromstring(response)
    channel = list(root)[0]
    items = filter(lambda item: item.tag == "item", list(channel))
    for item in items:

        title = list(filter(
            lambda child: child.tag == "title", list(item)
        ))[0].text.strip()

        link = list(filter(
            lambda child: child.tag == "link", list(item)
        ))[0].text

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
    printNow("Init...")
    home = os.path.expanduser("~")
    appName = "rss-download"
    configFile = home + "/.config/" + appName + "/config.json"
    cacheFolder = home + "/.cache/" + appName

    if not os.path.exists(cacheFolder):
        os.makedirs(cacheFolder)

    printNow("Init done")
    while True:
        printNow("Starting iteration...")
        config = json.load(open(configFile))
        for feed in list(config["feeds"]):
            process(cacheFolder, feed)

        sleepSeconds = config["pollIntervalSeconds"]
        printNow("Iteration done")
        printNow("Sleeping for", str(sleepSeconds), "seconds")
        time.sleep(sleepSeconds)


if __name__ == "__main__":
    main()
