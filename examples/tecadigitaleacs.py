import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader # import ../iiif_downloader.py
import logging

# DESCRIPTION:
# Read tecadigitaleacs.cultura.gov.it urls from .txt file
# Derive the manifest of the document
# For each manifest download the document

# Make main directory
maindir = 'tecadigitaleacs'
os.system('mkdir ' + maindir)

# Configure logger
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# From urls to manifests urls
url_file = 'tecadigitaleacs.txt'
manifests = []
with open(url_file) as f:
    for line in f:
        manifest_id = line.strip().split('/')[-1]
        manifest_url = 'https://acs.jarvis.memooria.org/meta/iiif/' + manifest_id + '/manifest'
        manifests.append(manifest_url)

downloader = iiif_downloader.IIIF_Downloader()
# For each manifest url
for i, manifest in enumerate(manifests):
    print('\033[95m' + '[' + str(i+1) + '/' + str(len(manifests)) + '] ' + manifest + '\033[0m')

    downloader.json_file = manifest
    downloader.maindir = maindir
    downloader.run()
