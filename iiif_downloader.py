import iiif
from re import match 
import argparse

def get_pages(pages):
  if(pages != 'all'):
    # Numbers > 0 separated by -
    pattern = r'^(?!0-0)([1-9]\d*)-([1-9]\d*)$'
    if(match(pattern, pages)):
      firstpage, lastpage = map(int, pages.split('-'))
      if(lastpage < firstpage):
        raise Exception("Invalid page range (invalid pages)")
    else:
      raise Exception("Invalid page range (invalid format)") 
  else:
    firstpage, lastpage = 1, -1
  return firstpage, lastpage

parser = argparse.ArgumentParser(description="IIIF Downloader", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-m", "--manifest", default='manifest', help="Manifest name or url")
parser.add_argument("-d", "--directory", default='.', help="Directory")
parser.add_argument("-p", "--pages", default='all', help="Page range (e.g. 3-27)")

args = parser.parse_args()
config = vars(args)

main_dir = config['directory']
manifest_name = config['manifest']
firstpage, lastpage = get_pages(config['pages'])

iiif.download_iiif_files_from_manifest(manifest_name, main_dir, firstpage, lastpage)
