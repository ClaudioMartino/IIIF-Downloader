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
for i in range(len(ver_dict[ver]['ids'])):
    file_name = 'manifests' + str(ver) + '/manifest' + str(i).zfill(2) + '.json'

    downloader = iiif_downloader.IIIF_Downloader()
    downloader.json_file = file_name
    logging.info(downloader.json_file)

    if(ver == '2'):
        reader = downloader.read_iiif_manifest2
    else:
        reader = downloader.read_iiif_manifest3

    with open(downloader.json_file) as f:
        infos = reader(json.load(f))

        na_cnt = 0
        for info in infos:
            if (len(info.id) == 0):
                na_cnt = na_cnt + 1
            else:
                for id_i in info.id:
                    if(not iiif_downloader.is_url(id_i)):
                        raise Exception(id_i + " is not an URL.")

        if(ver_dict[ver]['ids'][i]['tot'] != len(infos)):
            raise Exception("Wrong tot infos: " + str(len(infos)) + " instead of " + str(ver_dict[ver]['ids'][i]['tot']))

        if(ver_dict[ver]['ids'][i]['na'] != na_cnt):
            raise Exception("Wrong tot NA: " + str(na_cnt) + " instead of " + str(ver_dict[ver]['ids'][i]['na']))
