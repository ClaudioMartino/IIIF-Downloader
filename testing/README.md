# Testing

Tests are automatically executed each time a new code is pushed to the repository, as defined in [tests.yml](/.github/workflows/tests.yml). These tests are successful if no exception is raised.

The manifests present in the `manifests2` and `manifests3` directories are used to test the parsing functions. These manifests follows the 2.0 and the 3.0 standards and they should represent real world use cases. They have been downloaded from existing online libraries and from the official IIIF documentation. The sources are listed in [manifests2.txt](manifests2/manifests2.txt) and [manifests3.txt](manifests3/manifests3.txt).

Manifests have been archived in order to save space and must be extracted:

```
unzip manifests2/archive2.zip -d manifests2
unzip manifests3/archive3.zip -d manifests3
```

The [from_txt_to_json.py](from_txt_to_json.py) script can be used to download the manifests listed in the .txt files and to name them with progressive numbers:

```
python3 from_txt_to_json.py -v 2
python3 from_txt_to_json.py -v 3
```

## Manifest parsing

The functions that parse manifests (`read_iiif_manifest2` and `read_iiif_manifest3`) are tested with the files present in the directories.

To run the tests:

```
python3 test_read_manifest.py -v 2
python3 test_read_manifest.py -v 3
```

## Version checking

The function that read the version of the IIIF standard from the manifests (`get_version`) is tested with the files present in the directories.

```
python3 test_get_version.py -v 2
python3 test_get_version.py -v 3
```

## URI template matching

The function that check if strings conform to the URI template (`match_uri_pattern`) is tested with a list of sample URIs.

## File downloading

The function used to download files (`download_file`) is tested with a grayscale "Lenna".
