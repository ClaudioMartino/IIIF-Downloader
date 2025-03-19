#!/bin/bash

manifests=(
"https://api.irht.cnrs.fr/ark:/63955/fl685opg22dv/manifest.json"
"https://content.staatsbibliothek-berlin.de/dc/785884734/manifest"
"https://mss-cat.trin.cam.ac.uk/Manuscript/R.15.32/manifest.json"
"https://digitallibrary.unicatt.it/veneranda/data/public/manifests/0b/02/da/82/80/0a/f4/58/0b02da82800af458.json"
"https://www.e-rara.ch/i3f/v20/14575305/manifest"
"https://acs.jarvis.memooria.org/meta/iiif/bdd8df6f-dc05-431c-955a-be2078018553/manifest"
"https://adore.ugent.be/IIIF/manifests/archive.ugent.be%3A4B39C8CA-6FF9-11E1-8C42-C8A93B7C8C91"
"https://d.lib.ncsu.edu/collections/catalog/nubian-message-1992-11-30/manifest"
"https://iiif.bodleian.ox.ac.uk/iiif/manifest/60834383-7146-41ab-bfe1-48ee97bc04be.json"
"https://digital.library.villanova.edu/Item/vudl:92879/Manifest"
)

handle_sigint() {
    echo -e "\nNext iteration"
}

trap handle_sigint SIGINT

for m in "${manifests[@]}"; do
    echo "$m"
    ./iiif_downloader.py -m "$m"
done

