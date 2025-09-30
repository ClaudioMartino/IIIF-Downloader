# Testing

Unit tests have been implemented to check the validity of the parsing functions and the support functions.

The manifests present in the `manifests2` and `manifests3` directories are used to test the parsing functions. These manifests follows the 2.0 and the 3.0 standards and should represent real world use cases. They have been downloaded from existing online libraries and from the official IIIF documentation. The sources are listed in [manifests2.txt](manifests2/manifests2.txt) and [manifests3.txt](manifests3/manifests3.txt).

Manifests have been archived in order to save space and must be extracted before running the tests:
```
unzip manifests2/archive2.zip -d manifests2
unzip manifests3/archive3.zip -d manifests3
```

To run the unit tests:
```
python3 test_all.py
```

Use `-v` for a verbose output or `-q` for a quiet execution.

The [from_txt_to_json.py](from_txt_to_json.py) script can be used to download the manifests listed in the .txt files and to name them with progressive numbers:
```
python3 from_txt_to_json.py -v <IIIF-version>
```
