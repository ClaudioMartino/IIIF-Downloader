import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader # import ../iiif_downloader.py
import json
import logging
import argparse
from test_common import ver_dict

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Parse arguments
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-v", default='3')
config = vars(parser.parse_args())
ver = config['v']

# Read manifests
for i in range(ver_dict[ver]['tot']):
    file_name = 'manifests' + str(ver) + '/manifest' + str(i).zfill(2) + '.json'
    logging.info(file_name)
    with open(file_name) as f:
        ver2 = iiif_downloader.get_iiif_version(json.load(f))
        if (ver2 != int(ver)):
            raise Exception("Read " + str(ver2) + ", expected " + ver)
