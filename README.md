# Download all the images from an IIIF manifest

IIIF is the [International Image Interoperability Framework](https://iiif.io/), a set of open standards for digital objects online.

Most of the scripts out there ask you to install plenty of heavy external libraries in order to download the files.

This script needs only urllib!

## Basic usage

You run it as:

```
python3 iiif_downloader.py -m manifest [-d directory]
```

And that's all.

![Screenshot of the downloader.](img.png)

## Advanced usage

All the functions have been defined in `iiif.py`, you can include it in your project and run more complicated tasks. Have a look at the example directory.
