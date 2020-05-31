#!/usr/bin/env python3
"""xkcdDL - Download xkcd comics"""

# --------------------------------------------------------------------------- #
# IMPORTS
import sys
import os
import json
import shutil
import time
import argparse
import colored
import requests
# ########################################################################### #


# --------------------------------------------------------------------------- #
VERSION = "0.2"
NAME = "xkcdDL"
# ########################################################################### #


# --------------------------------------------------------------------------- #
# CONSTANTS
BOLD = colored.attr("bold")
RESET = colored.attr("reset")
RED = colored.fg("red")
GREEN = colored.fg("green")
BOLDRED = BOLD + RED
BOLDGREEN = BOLD + GREEN
HEADERS = {'User-Agent': "{}/{}".format(NAME, VERSION)}
# ########################################################################### #


# --------------------------------------------------------------------------- #
def main(args):
    """Main function
    Args:
        args (list): List of arguments
    """

    parser = ArgumentParser()
    parser.add_argument("-i", "--image", action="store_const", dest="image", const=True, default=False, help="Save image(s) only")
    parser.add_argument("-j", "--json", action="store_const", dest="json", const=True, default=False, help="Save JSON file(s) only")
    parser.add_argument("-d", "--delay", type=float, dest="sec", default=0.5, help="Seconds of delay between comic requests (default: 0.5sec)")
    parser.add_argument('N', nargs='*', help="Comic number(s) or range(s) (e.g. 1045 or 56-129)")
    args = parser.parse_args()

    if args.N:
        #Split ranges and cast number to integer
        comics = []
        for c in args.N:
            comic = [int(i) for i in c.split('-')]
            comics.append(comic)
    else:
        #Find missing comics
        try:
            comics = findMissing()
        except requests.exceptions.RequestException as e:
            parser.error("Unable to get info of latest comic ({})".format(str(e)))
        except NoMissingException:
            print('{}No new or missing comics{}'.format(BOLDGREEN, RESET))
            return

    print('{}Downloading comics...{}'.format(BOLD, RESET))

    for comic in comics:
        if len(comic) > 1:
            for i in range(comic[0], comic[1]+1):
                download(i, (not args.json), (not args.image))
                time.sleep(args.sec)
        else:
            download(comic[0], (not args.json), (not args.image))
            time.sleep(args.sec)

    print('{}Done!{}'.format(BOLDGREEN, RESET))
# ########################################################################### #

# --------------------------------------------------------------------------- #
def findMissing():
    """Find new and missing comics and return their numbers as a list or raises
    exceptions if no comics are missing

    Raises:
        requests.exceptions.RequestException: Lookup of latest comic failed
        NoMissingException: No missing/new comics
    """
    #Get number of latest comic
    r = requests.get('https://xkcd.com/info.0.json', headers=HEADERS)
    r.raise_for_status()
    content = r.json()
    latest = content["num"]
    del r

    #Find missing JSONs
    missing = []
    for i in range(1, latest+1):
        if not os.path.isfile("{}.json".format(i)):
            missing.append([i])

    #Remove 404 as this comic does not exist
    missing.remove([404])

    #Raise exception if no items in missing
    if not missing:
        raise NoMissingException()

    #Return missing items
    return missing
# ########################################################################### #

# --------------------------------------------------------------------------- #
def download(number, dlImg, dlJson):
    """Download files
    Args:
        number (int): The comic number to download
        dlImg (bool): Whether to download and save the image or not
        dlJson (bool): Whether to save the JSON or not
    """
    print("Downloading #{}".format(number))

    #Download JSON
    r = requests.get('https://xkcd.com/{}/info.0.json'.format(number), headers=HEADERS)
    if r.status_code == 200:
        content = r.json()
        del r
    else:
        print('{}Error: {}{}'.format(BOLDRED, r.status_code, RESET))
        return

    #Download and save image
    if dlImg:
        url = content["img"]
        ext = url.split('.')[-1]
        url2x = "{}_2x.{}".format(url[:-(len(ext)+1)], ext)
        name = "{}.{}".format(number, ext)

        try:
            r = requests.get(url2x, stream=True, headers=HEADERS)
            r.raise_for_status()
            with open(name, 'wb') as imgFile:
                shutil.copyfileobj(r.raw, imgFile)
            content["img_2x"] = url2x
        except requests.exceptions.RequestException:
            try:
                r = requests.get(url, stream=True, headers=HEADERS)
                r.raise_for_status()
                with open(name, 'wb') as imgFile:
                    shutil.copyfileobj(r.raw, imgFile)
            except requests.exceptions.RequestException:
                print('{}Unable to download image at "{}" (Error: {}){}'.format(BOLDRED, url, r.status_code, RESET))
        del r

    #Save JSON
    if dlJson:
        jsonFileName = "{}.json".format(number)
        with open(jsonFileName, "w") as jsonFile:
            json.dump(content, jsonFile, indent=4)
# ########################################################################### #


# ########################################################################### #
class ArgumentParser(argparse.ArgumentParser):
    """ArgumentParser subclass that prints colored error messages"""
    def error(self, message):
        self.exit(2, "{}ERROR: {}{}\n".format(BOLDRED, message, RESET))
# --------------------------------------------------------------------------- #


# ########################################################################### #
class NoMissingException(Exception):
    """No missing or new comics"""
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# Default
if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print('{}Aborted!{}'.format(BOLDRED, RESET))
# ########################################################################### #
