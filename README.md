# Download all the images from an IIIF manifest

IIIF is the [International Image Interoperability Framework](https://iiif.io/), a set of open standards for digital objects online.

Most of the Python scripts out there ask you to install plenty of heavy external libraries. This script needs only standard libraries!

It works with the [2.0 API](https://iiif.io/api/presentation/2.0) and the [3.0 API](https://iiif.io/api/presentation/3.0).

## Basic usage

Run the script as:

```
python3 iiif_downloader.py [-m manifest]
```

All the images of the document with the default quality, not cropped, and not scaled, will be downloaded on your computer, named with a progressive number (`p001.jpg` et cetera).

The manifest can be a file on your computer or a http(s) link. `manifest` is the default value. You can also use a collection of manifests, the script will recognize it and download all the files from the manifests in different directories.

![Screenshot of the downloader.](img.png)

## Other options

* You can specify the output directory with `-d directory`. The default value is the current directory (`.`).
* You can specify the range of the pages to download with `-p first-last` (e.g. `-p 10-20` for pages from 10 to 20, or `-p 10-10` for page 10 only).
* You can use the `-f` flag to force overwriting the files when they are already present in your directory.
* You can use the `--use-labels` flag to name the files with the manifest labels, instead of a progressive number.

All the options can be displayed by running the helper (`iiif_downloader.py -h`).

## Advanced usage

All the functions have been defined in `iiif.py`, you can include it in your project and run more complicated tasks. Have a look at the example directory.

## Testings
The script has been tested with the manifests and the collections listed in the `testing` directory.
