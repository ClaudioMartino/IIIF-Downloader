# IIIF Downloader
A Python 3 script to download all the images from an IIIF manifest.

IIIF is the [International Image Interoperability Framework](https://iiif.io/), a set of open standards for digital objects online. Most of the Python scripts out there ask you to install plenty of heavy external libraries. This script needs only standard libraries! It works with the [2.0](https://iiif.io/api/presentation/2.0) and the [3.0](https://iiif.io/api/presentation/3.0) standards.

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/) [![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/license/MIT) [![Tests status](https://github.com/ClaudioMartino/IIIF-Downloader/actions/workflows/tests.yml/badge.svg)](https://github.com/ClaudioMartino/IIIF-Downloader/actions)

## Basic usage

Run the script as:

```
python3 iiif_downloader.py -m manifest
```

All the images of the document with the default quality, not cropped, and not scaled, will be downloaded on your computer, named with a progressive number (`p001.jpg` et cetera).

The manifest can be a file on your computer or a http(s) link. `manifest` is the default value. You can also use a collection of manifests: the script will recognize it and download all the files from the manifests in different directories.

![Screenshot of the downloader.](img.png)

## Other options

* You can specify the output directory with `-d directory`. The default value is the working directory (`.`).
* You can specify the range of the pages you want to download with `-p first-last` (e.g. `-p 10-20` for pages from 10 to 20, or `-p 10-10` for page 10 only).
* You can use the `-f` option to force overwriting the files when they are already present in your directory.
* You can use the `--use-labels` option to name the files with the manifest labels, instead of a progressive number.
* Use the `-v` option to print more information.

All these options can be displayed by running the helper with `-h`.

## Advanced usage

You can include the library in your project and run more complicated tasks. You can also set what level of log messages you want to record. Have a look at the [examples](examples) directory.

## Testing

The script has been tested with the manifests listed in the [testing](testing) directory.

## Contributing

Contributions are most welcome by forking the repository and sending a pull request. Errors and new features proposals can be reported [opening an issue](https://github.com/ClaudioMartino/IIIF-Downloader/issues/new/choose) as well.
