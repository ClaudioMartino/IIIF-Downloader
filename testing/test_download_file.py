import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader # import ../iiif_downloader.py
import json
import logging

# Configure logger
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# Download Lenna
src_url = 'https://raw.githubusercontent.com/ClaudioMartino/IIIF-Downloader/refs/heads/main/testing/lenna.jpg'
target_name = 'lenna_downloaded.jpg'

status = iiif_downloader.download_file(src_url, target_name)

logging.info(status)

if os.path.exists(target_name):
    os.remove(target_name) 
