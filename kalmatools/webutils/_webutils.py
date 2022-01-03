#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import math
import os
import traceback
import urllib.request

import requests
from bs4 import BeautifulSoup

__version__ = "0.0.1"


def getChromecastImages():

    images = {}

    URL = "https://raw.githubusercontent.com/dconnolly/chromecast-backgrounds/master/backgrounds.json"
    headers = {'Accept-Encoding': 'identity'}
    try:
        with requests.get(URL, timeout=20, headers=headers) as response:
            page = response.json()
    except:
        print("Error getting HTML page from:", URL)
        print(traceback.format_exc())
        return images

    images["chromecast"] = page

    return images


def getBingImages():

    images = []

    URL = "https://bing.gifposter.com/list/new/desc/slide.html?p=1"
    headers = {'Accept-Encoding': 'identity'}
    try:
        with requests.get(URL, timeout=20, headers=headers) as response:
            page = response.text
    except:
        print("Error getting HTML page from:", URL)
        print(traceback.format_exc())
        return images

    soup = BeautifulSoup(page, 'html.parser')

    imgEntries = soup.find_all('a', attrs={'itemprop':'contentUrl'})

    for image in imgEntries:
        images.append(image.get('href'))

    return images


def getBingTodayImage():

    image = ""

    URL = "https://bing.gifposter.com"
    headers = {'Accept-Encoding': 'identity'}
    try:
        with requests.get(URL, timeout=20, headers=headers) as response:
            page = response.text
    except:
        print("Error getting HTML page from:", URL)
        print(traceback.format_exc())
        return image

    soup = BeautifulSoup(page, 'html.parser')
    image = soup.find("meta", attrs={"name":"twitter:image"})["content"]

    return image


def download(url: str, filename: str):
    # https://stackoverflow.com/questions/56950987/download-file-from-url-and-save-it-in-a-folder-python

    dest_folder = str(os.sep + filename).rsplit(os.sep)[0]
    if dest_folder and not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    r = requests.get(url, stream=True, timeout=20)
    if r.ok:
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:
        r.raise_for_status()


def httpPing(url):
    try:
        r = requests.get(url, timeout=20)
    except:
        return False
    return r.ok


def get_coordinates(city, state="", country=""):

    q = str(city) + str("," + state if state else "") + str("," + country if country else "")
    url = 'http://nominatim.openstreetmap.org/search?q=%s&format=json&addressdetails=1' % q

    coordinates = []
    try:
        with urllib.request.urlopen(url) as data:
            resp = json.loads(data.read().decode('utf8'))

        for i in range(20):
            try:
                coordinates.append([resp[i]["display_name"], resp[i]["lat"], resp[i]["lon"]])
            except:
                break
    except:
        pass

    return coordinates


def get_location_by_ip(lang="en"):

    url = 'http://ip-api.com/json/?lang=%s' % lang

    ret = []
    try:
        with urllib.request.urlopen(url) as data:
            resp = json.loads((data.read().decode('utf8')))

        if resp["status"] == "success":
            ret = [resp["city"], resp["regionName"], resp["country"], resp["lat"], resp["lon"]]
    except:
        pass

    return ret


# Units
METRIC = 'metric'
IMPERIAL = 'imperial'
def get_distanceByCoordinates(origin, destination, units=METRIC):

    lat1, lon1 = origin
    lat2, lon2 = destination
    if units == METRIC:
        radius = 6371  # km
    elif units == IMPERIAL:
        radius = 6371 * 0.6213712  # miles
    else:
        return -1

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def get_distanceByName(origin, destination, units=METRIC):

    city, state, country = origin
    _, lat1, lon1 = get_coordinates(city, state, country)
    city, state, country = destination
    _, lat2, lon2 = get_coordinates(city, state, country)

    if units == METRIC:
        radius = 6371  # km
    elif units == IMPERIAL:
        radius = 6371 * 0.6213712  # miles
    else:
        return -1

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d
