#!/bin/bash

manifests=(
"https://iiif.io/api/cookbook/recipe/0001-mvm-image/manifest.json"
"https://iiif.io/api/cookbook/recipe/0004-canvas-size/manifest.json"
"https://iiif.io/api/cookbook/recipe/0005-image-service/manifest.json"
"https://iiif.io/api/cookbook/recipe/0006-text-language/manifest.json"
"https://iiif.io/api/cookbook/recipe/0118-multivalue/manifest.json"
"https://iiif.io/api/cookbook/recipe/0007-string-formats/manifest.json"
"https://iiif.io/api/cookbook/recipe/0029-metadata-anywhere/manifest.json"
"https://iiif.io/api/cookbook/recipe/0008-rights/manifest.json"
"https://iiif.io/api/cookbook/recipe/0009-book-1/manifest.json"
"https://iiif.io/api/cookbook/recipe/0011-book-3-behavior/manifest-continuous.json"
"https://iiif.io/api/cookbook/recipe/0299-region/manifest.json"
"https://iiif.io/api/cookbook/recipe/0010-book-2-viewing-direction/manifest-rtl.json"
"https://iiif.io/api/cookbook/recipe/0283-missing-image/manifest.json"
"https://iiif.io/api/cookbook/recipe/0117-add-image-thumbnail/manifest.json"
"https://iiif.io/api/cookbook/recipe/0202-start-canvas/manifest.json"
"https://iiif.io/api/cookbook/recipe/0230-navdate/navdate-collection.json"
"https://iiif.io/api/cookbook/recipe/0154-geo-extension/manifest.json"
"https://iiif.io/api/cookbook/recipe/0240-navPlace-on-canvases/manifest.json"
"https://iiif.io/api/cookbook/recipe/0234-provider/manifest.json"
"https://iiif.io/api/cookbook/recipe/0032-collection/collection.json"
)

handle_sigint() {
    echo -e "\nNext iteration"
}

trap handle_sigint SIGINT

for m in "${manifests[@]}"; do
    echo "$m"
    ./iiif_downloader.py -m "$m" -f
done

