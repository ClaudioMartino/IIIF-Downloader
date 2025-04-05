import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader # import ../iiif_downloader.py
import json
import logging
import argparse

#url_file = 'manifests2.txt'
#manifests = []
#with open(url_file) as f:
#    for manifest_url in f:
#        manifests.append(manifest_url.strip())
#for i, manifest in enumerate(manifests):
#    iiif_downloader.download_file(manifest, "manifest" + str(i).zfill(2) + ".json")

api_dict = {
    '2': {
        'reader': iiif_downloader.read_iiif_manifest2,
        'tot': 10
    },
    '3': {
        'reader': iiif_downloader.read_iiif_manifest3,
        'tot': 18
    }
}

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Parse arguments
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--api", default='3')
config = vars(parser.parse_args())
api = config['api']

# Read manifests
for i in range(api_dict[api]['tot']):
    file_name = 'manifests' + str(api) + '/manifest' + str(i).zfill(2) + '.json'
    logging.info(file_name)
    with open(file_name) as f:
        manifest_label, manifest_id, infos = api_dict[api]['reader'](json.load(f))
