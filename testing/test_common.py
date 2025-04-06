import iiif_downloader

ver_dict = {
    "2": {
        'dir': 'manifests2',
        'txt': 'manifests2.txt',
        "reader": iiif_downloader.read_iiif_manifest2,
        "tot": 11
    },

    "3": {
        'dir': 'manifests3',
        'txt': 'manifests3.txt',
        "reader": iiif_downloader.read_iiif_manifest3,
        "tot": 19
    }
}
