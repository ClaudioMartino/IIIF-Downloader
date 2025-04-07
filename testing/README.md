# Testing

Tests are automatically executed each time a new code is pushed to the repository, as defined in [tests.yml](/.github/workflows/tests.yml). These tests are successful if no exception is raised.

The [from_txt_to_json.py](from_txt_to_json.py) script can be used to download the manifests listed in a .txt file and to name them with progressive numbers.

## Manifest parsing

The functions that parse manifests (`read_iiif_manifest2` and `read_iiif_manifest3`) are tested with the .json files present in the `manifests2` and `manifests3` directories. These manifests follows the 2.0 and the 3.0 standards and they should represent real world use cases. They have been downloaded from existing online libraries and from the IIIF official documentation. The sources are listed in [manifest2.txt](manifests2/manifests2.txt) and [manifest3.txt](manifests3/manifests3.txt). Manifests have been archived in order to save space.

To run the tests (manifests must be unzipped first):

```
python3 test_read_manifest.py -v version
```

## Version checking

The function that read the version of the IIIF standard from the manifests (`get_version`) is tested with the files present in the directories.

To run the tests:

```
python3 test_get_version.py -v version
```

## File downloading

The function used to download a file (`download_file`) is tested with a grayscale "Lenna".
