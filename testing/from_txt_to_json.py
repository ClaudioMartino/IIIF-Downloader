import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader # import ../iiif_downloader.py

# read remote manifests from url in .txt
#url_file = 'manifests2/manifests2.txt'
url_file = 'manifests3/manifests3.txt'
manifests = []
with open(url_file) as f:
    for manifest_url in f:
        manifests.append(manifest_url.strip())

# Download them in .json files
for i, manifest in enumerate(manifests):
    iiif_downloader.download_file(manifest, "manifest" + str(i).zfill(2) + ".json")
