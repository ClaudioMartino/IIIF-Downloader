import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader  # import ../iiif_downloader.py
import argparse
import logging

# DESCRIPTION:
# Read tecadigitaleacs.cultura.gov.it URLs from input file (-i)
# Derive the manifest of the document from URL
# For each manifest download the document

# Make main directory
maindir = 'tecadigitaleacs'
os.system('mkdir ' + maindir)

# Configure parser
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-i", metavar="<file>", required=True,
    help="Input file with one URL on each line")
parser.add_argument(
    "-f", "--force", action="store_true", help="Overwrite existing files")
parser.add_argument(
    "-h", "--help", action="help", help="Print this help message and exit")
config = vars(parser.parse_args())

# Configure logger
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# Derive manifest from URLs
manifest_list = []
with open(config["i"]) as f:
    for line in f:
        manifest_id = line.strip().split('/')[-1]
        manifest_url = "https://acs.jarvis.memooria.org/meta/iiif/" + \
            manifest_id + "/manifest"
        manifest_list.append(manifest_url)

# Create Downloader
downloader = iiif_downloader.IIIF_Downloader()
downloader.maindir = maindir
downloader.force = config["force"]

# Loop over each manifest and download the whole document
for i, manifest in enumerate(manifest_list):
    print("\033[95m" + "[" + str(i + 1) + "/" + str(len(manifest_list)) +
          "] " + manifest + "\033[0m")
    downloader.json_file = manifest
    downloader.run()
