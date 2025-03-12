import iiif 
import argparse

parser = argparse.ArgumentParser(description="IIIF Downloader", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-m", "--manifest", default='manifest', help="Manifest name")
parser.add_argument("-d", "--directory", default='.', help="Directory")

args = parser.parse_args()
config = vars(args)

main_dir = config['directory']
manifest_name = config['manifest']

iiif.download_iiif_files_from_manifest(manifest_name, main_dir)
