import os
import logging
import pprint

from PIL import Image
import requests
from bs4 import BeautifulSoup

# Globals
################################################################################

PICTURES_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]

# Functions
################################################################################

def initLog(name):

    # Create logger with 'spam_application'
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('debug.log')
    fh.setLevel(logging.INFO)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s | %(name)s | [%(levelname)s] | %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)

    return log


def isValidPictureUrl(url):
    path, file = os.path.split(url)
    name, ext = os.path.splitext(file)

    if ext in PICTURES_EXTENSIONS:
        return True
    else:
        return False


def getPicturesFromURL(url):

    pictures = []
    x = requests.get(url)
    soup = BeautifulSoup(x.text, features="html.parser")

    for link in soup.find_all("img"):

        large_file = link.get("data-large-file")
        if large_file:
            pictures.append(large_file)
            continue

        src = link.get("src")
        if src:
            pictures.append(src)

    return pictures


def picturesToGallery(urls, heights):

    dict_gallery = {}

    column_height = [0, 0, 0, 0]

    nb_urls = len(urls)

    for i in range(nb_urls):

        min_value = min(column_height)
        index = column_height.index(min_value)

        height = float(heights[i])

        column_height[index] += height

        dict_gallery[i] = {"url": urls[i],
                           "column": index + 1}

    return dict_gallery


def openImage(url):

    im = None

    from_internet = False

    if url[:5] in ["http:", "https"]:
        from_internet = True

    file_name, ext = os.path.splitext(url)

    # Open Image
    if ext == ".png":
        if from_internet:
            path = requests.get(url, stream=True).raw
            image = Image.open(path)
        else:
            image = Image.open(url)

        im = Image.composite(image, Image.new('RGB', image.size, 'white'),
                             image)

    elif ext in PICTURES_EXTENSIONS:
        if from_internet:
            path = requests.get(url, stream=True).raw
            im = Image.open(path)
        else:
            im = Image.open(url)

    return im

# TEST
################################################################################

# URL_TEST = "https://www.iamag.co/the-art-of-arthus-pilorget"
#
# pics = getPicturesFromURL(URL_TEST)
#
# pprint.pprint(picturesToGallery(pics))
