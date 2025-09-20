#!/usr/bin/python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader  # import ../iiif_downloader.py
import logging
from re import search
import argparse

# DESCRIPTION:
# Read https://antenati.cultura.gov.it urls from .txt file
# Derive the manifest of the document
# For each manifest download the document

# Make main directory
maindir = 'antenati'
os.system('mkdir ' + maindir)

# Configure parser for user defined command line options
parser = argparse.ArgumentParser(add_help=False)

general = parser.add_argument_group("General options")
general.add_argument(
    "-f", "--force", action="store_true",
    help="Overwrite existing files")
general.add_argument(
    "-h", "--help", action="help",
    help="Print this help message and exit")

config = vars(parser.parse_args())

c = iiif_downloader.Conf()
c.width = None
c.force = config["force"]
c.referer = "https://antenati.cultura.gov.it/"

# Configure logger
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# From urls to manifests urls
url_file = 'antenati.txt'
manifests = []
with open(url_file) as f:
    for antenati_page in f:
        response = iiif_downloader.open_url(antenati_page)
        html_content = response.read().decode("utf-8").splitlines()
        for line in html_content:
            if ('manifestId' in line):
                manifest_line = line
                break
        manifest_url_pattern = search(r'\'([A-Za-z0-9.:/-]*)\'', manifest_line)
        manifest_url = manifest_url_pattern.group(1)
        logging.info(manifest_url + " found in " + antenati_page.rstrip())
        manifests.append(manifest_url)

# For each manifest url
for i, manifest in enumerate(manifests):
    logging.info(
        "\033[95m" + "[" + str(i+1) + "/" + str(len(manifests)) + "] " +
        manifest + '\033[0m')

    iiif_downloader.download_iiif_files(manifest, maindir, c)
