import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader # import ../iiif_downloader.py
import json
import logging
import argparse
from test_common import ver_dict

# Configure logger
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# Parse arguments
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-v", default='3')
config = vars(parser.parse_args())
ver = config['v']

# Read manifests
for i in range(len(ver_dict[ver]['ids'])):
    file_name = 'manifests' + str(ver) + '/manifest' + str(i).zfill(2) + '.json'
    logging.info(file_name)
    with open(file_name) as f:
        manifest_label, manifest_id, infos = ver_dict[ver]['reader'](json.load(f))

        na_cnt = 0
        for info in infos:
            if (info.id == 'NA'):
                na_cnt = na_cnt + 1

        #print("{ \"tot\" : " + str(len(infos))+ ", \"na\": " + str(na_cnt) + " }")

        if(ver_dict[ver]['ids'][i]['tot'] != len(infos)):
            raise Exception("Wrong tot infos: " + str(len(infos)) + " instead of " + str(ver_dict[ver]['ids'][i]['tot']))
        if(ver_dict[ver]['ids'][i]['na'] != na_cnt):
            raise Exception("Wrong tot NA: " + str(na_cnt) + " instead of " + str(ver_dict[ver]['ids'][i]['na']))
