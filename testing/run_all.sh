#!/bin/bash

echo "- Unzip manifests"
unzip manifests2/archive2.zip -d manifests2
unzip manifests3/archive3.zip -d manifests3
#mkdir manifests2/tmp
#unzip manifests2/archive.zip -d manifests2/tmp
#for f in ./manifests2/tmp/*.json; do
#    mv "$f" "manifests2"
#done
#rm -rf manifests2/tmp

echo "- Test download"
python3 test_download_file.py

echo "- Test get version"
python3 test_get_version.py -v 2
python3 test_get_version.py -v 3

echo "- Test read manifest"
python3 test_read_manifest.py -v 2
python3 test_read_manifest.py -v 3

#echo "- Remove unzipped manifests"
rm manifests2/*.json
rm manifests3/*.json
