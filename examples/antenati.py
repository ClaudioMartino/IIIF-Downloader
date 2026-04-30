import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader  # import ../iiif_downloader.py
import argparse
import logging
from re import search

# DESCRIPTION:
# Read https://antenati.cultura.gov.it URLs from input file (-i)
# - Download the single page
# OR
# - Find the manifest and download the whole document (-a/--all-pages)
# NB: info.json widths are used.

# Make main directory
subdir = 'antenati'
os.system('mkdir ' + subdir)

# Configure parser
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-i", metavar="<file>", required=True,
    help="Input file with one URL on each line")
parser.add_argument(
    "-a", "--all-pages", action="store_true",
    help="Download the whole document to whom the page belong")
parser.add_argument(
    "-f", "--force", action="store_true", help="Overwrite existing files")
parser.add_argument(
    "-h", "--help", action="help", help="Print this help message and exit")
config = vars(parser.parse_args())

# Create downloader
downloader = iiif_downloader.IIIF_Downloader()
downloader.force = config["force"]
downloader.width = None  # -w without argument, we want the info.json width
downloader.referer = "https://antenati.cultura.gov.it/"
downloader.maindir = subdir

# Configure logger
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# Open input file
with open(config["i"]) as f:
    lines = f.readlines()
    # Loop over each URL
    for i, antenati_page in enumerate(lines):
        antenati_page = antenati_page.rstrip()  # remove newline
        logging.info(
            "\033[95m" + "[" + str(i+1) + "/" + str(len(lines)) + "] " +
            antenati_page + '\033[0m')

        if (not config["all_pages"]):
            # Derive service ID from page code
            code_antenati = antenati_page.split('/')[-1]
            service_id = "https://iiif-antenati.cultura.gov.it/iiif/2/" + \
                code_antenati

            # Look for width in info.json
            info = iiif_downloader.Page()
            info.w = None
            downloader.check_image_information_width(service_id, info)

            # Download single page
            filename = code_antenati + ".jpg"
            subdir_filename = subdir + "/" + filename
            if (os.path.exists(subdir_filename) and not downloader.force):
                logging.info(
                    subdir_filename +
                    " exists, skip. Use -f to force overwrite the files.")
            else:
                image_url = "https://iiif-antenati.cultura.gov.it/iiif/2/" + \
                    code_antenati + "/full/" + str(info.w) + ",/0/default.jpg"
                filesize = iiif_downloader.download_file(
                    image_url, subdir + "/" + filename, downloader.referer)
                if (filesize > 0):
                    logging.info(
                        "\033[92m" + filename + " (" +
                        str(round(filesize / 1000)) + " kB) saved in " +
                        subdir + "\033[0m")
        else:
            # Look for manifest URL in HTML page
            response = iiif_downloader.open_url(antenati_page)
            html_content = response.read().decode("utf-8").splitlines()
            for line in html_content:
                if ('manifestId' in line):
                    manifest_line = line
                    break
            manifest_url_pattern = search(
                r'\'([A-Za-z0-9.:/-]*)\'', manifest_line)
            manifest_url = manifest_url_pattern.group(1)
            logging.info(
                "Manifest " + manifest_url + " found in " + antenati_page)

            # Download whole document
            downloader.json_file = manifest_url
            downloader.run()
