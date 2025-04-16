import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader # import ../iiif_downloader.py
import argparse
from test_common import ver_dict

# Parse arguments
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-v", default='3')
config = vars(parser.parse_args())
ver = config['v']

# read remote manifests from url in .txt
manifests = []
with open(ver_dict[ver]['dir'] + '/' + ver_dict[ver]['txt']) as f:
    for manifest_url in f:
        manifests.append(manifest_url.strip())

# Download them in .json files
for i, manifest in enumerate(manifests):
    print(manifest)
    output_file = ver_dict[ver]['dir'] + '/' + "manifest" + str(i).zfill(2) + ".json"
    if(not os.path.isfile(output_file)):
        iiif_downloader.download_file(manifest, output_file)
    else:
        print("File exists, skip.")
