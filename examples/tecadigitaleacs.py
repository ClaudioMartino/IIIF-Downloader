import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif # import ../iiif.py

# DESCRIPTION:
# Read tecadigitaleacs.cultura.gov.it urls from .txt file
# For each url download document in subdirectories

#TODO skip download of manifest.json

# From urls to manifests urls
url_file = 'tecadigitaleacs.txt'
manifests = []
with open(url_file) as f:
    for line in f:
        manifest_id = line.strip().split('/')[-1]
        manifest_url = 'https://acs.jarvis.memooria.org/meta/iiif/' + manifest_id + '/manifest'
        manifests.append(manifest_url)

# Make main directory
maindir = 'tecadigitaleacs'
os.system('mkdir ' + maindir)

# For each manifest url
for i, manifest in enumerate(manifests):
    print('\033[95m' + '[' + str(i+1) + '/' + str(len(manifests)) + '] ' + manifest + '\033[0m')

    # Download manifest file
    manifest_name = 'manifest.json'
    if(os.path.isfile(manifest_name)):
        os.remove(manifest_name)
    iiif.download_file(manifest, manifest_name)

    # Download files in maindir/label directory
    iiif.download_iiif_files_from_manifest(manifest_name, maindir)

    # Remove manifest file
    os.remove(manifest_name)
