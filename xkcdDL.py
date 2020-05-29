#!/usr/bin/env python3
"""xkcdDL - Download xkcd comics"""

# --------------------------------------------------------------------------- #
# IMPORTS
import sys
import json
import shutil
import colored
import requests
# ########################################################################### #


# --------------------------------------------------------------------------- #
# CONSTANTS
BOLD = colored.attr("bold")
RESET = colored.attr("reset")
RED = colored.fg("red")
GREEN = colored.fg("green")
BOLDRED = BOLD + RED
BOLDGREEN = BOLD + GREEN
# ########################################################################### #


# --------------------------------------------------------------------------- #
def main(args):
    """Main function
    Args:
        args (list): List of arguments
    """
    if not args:
        print('{}No comics specified for download{}'.format(BOLDRED, RESET))
        printHelp()
        return

    dlImg = True
    dlJson = True
    comics = []

    for arg in args:
        try:
            comic = [int(i) for i in arg.split('-')]
            comics.append(comic)
        except ValueError:
            if arg in ('-h', '--help'):
                printHelp()
                return
            if arg in ('-i', '--images'):
                dlJson = False
            elif arg in ('-j', '--jsons'):
                dlImg = False
            else:
                print('{}Unknown argument: "{}"{}'.format(BOLDRED, arg, RESET))
                printHelp()
                return

    if not comics:
        print('{}No comics specified for download{}'.format(BOLDRED, RESET))
        printHelp()
        return

    print('{}Downloading comics...{}'.format(BOLD, RESET))

    for comic in comics:
        if len(comic) > 1:
            for i in range(comic[0], comic[1]+1):
                download(i, dlImg, dlJson)
        else:
            download(comic[0], dlImg, dlJson)

    print('{}Done!{}'.format(BOLDGREEN, RESET))
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
    r = requests.get('https://xkcd.com/{}/info.0.json'.format(number))
    if r.status_code == 200:
        content = r.json()
        if dlJson:
            jsonFileName = "{}.json".format(number)
            with open(jsonFileName, "w") as jsonFile:
                json.dump(content, jsonFile, indent=4)
        del r
    else:
        print('{}Error: {}{}'.format(BOLDRED, r.status_code, RESET))
        return

    #Download image
    if dlImg:
        url = content["img"]
        ext = url.split('.')[-1]
        url2x = "{}_2x.{}".format(url[:-(len(ext)+1)], ext)
        name = "{}.{}".format(number, ext)

        try:
            r = requests.get(url2x, stream=True)
            r.raise_for_status()
            with open(name, 'wb') as imgFile:
                shutil.copyfileobj(r.raw, imgFile)
        except requests.exceptions.RequestException:
            try:
                r = requests.get(url, stream=True)
                r.raise_for_status()
                with open(name, 'wb') as imgFile:
                    shutil.copyfileobj(r.raw, imgFile)
            except requests.exceptions.RequestException:
                print('{}Unable to download image at "{}" (Error: {}){}'.format(BOLDRED, url, r.status_code, RESET))
        del r
# ########################################################################### #


# --------------------------------------------------------------------------- #
def printHelp():
    """Print help"""
    print("xkcdDL -- Download xkcd comic images and info JSONs\n")
    print("Usage: xkcdDL [-i][-j] N [N...]\n")
    print("Options:")
    print("\t-i: Save images only")
    print("\t-j: Save JSONs only")
    print("\nN: Comic number or range (e.g. 1045 or 56-129)")
# ########################################################################### #


# --------------------------------------------------------------------------- #
# Default
if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('{}Aborted!{}'.format(BOLDRED, RESET))
# ########################################################################### #
