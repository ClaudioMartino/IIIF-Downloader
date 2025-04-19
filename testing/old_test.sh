#!/bin/bash

# Run it as: ./run.sh manifest_list.txt
# You can stop one iteration of the loop with ctrl+c

handle_sigint() {
    echo -e "\nNext manifest"
}

trap handle_sigint SIGINT

while IFS= read -r m; do
    echo "$m"
    python3 ../iiif_downloader.py -m "$m"
done < "$1"
