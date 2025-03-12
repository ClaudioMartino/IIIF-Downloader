# Download all the images from an IIIF manifest

IIIF is the [International Image Interoperability Framework](https://iiif.io/), a set of open standards for digital objects online.

Most of the scripts out there ask you to install plenty of heavy external libraries in order to download the files. This script needs only urllib!

For now it works with the [2.0 API](https://iiif.io/api/presentation/2.0) only, and not even with all the manifests, but I am working on it. You can test it with manifests from the [Bodleian Library](http://iiif.bodleian.ox.ac.uk/iiif/manifest/60834383-7146-41ab-bfe1-48ee97bc04be.json), the [Ghent University](http://adore.ugent.be/IIIF/manifests/archive.ugent.be%3A4B39C8CA-6FF9-11E1-8C42-C8A93B7C8C91), the [Archivio Centrale dello Stato](https://acs.jarvis.memooria.org/meta/iiif/bdd8df6f-dc05-431c-955a-be2078018553/manifest), and the [National Gallery of Art](https://media.nga.gov/public/manifests/nga_highlights.json). 

## Basic usage

You run the script as:

```
python3 iiif_downloader.py [-m manifest]
```

The manifest can be a file on your computer or a http(s) link. `manifest` is the default value.

![Screenshot of the downloader.](img.png)

## Other options

* Specify the output directory with `-d directory`.
* Specify the range of the pages to download with `-p first-last` (e.g. `10-20` for pages from 10 to 20, or `10-10` for page 10 only).
* Use the `--use-page-numbers` flag to name the files with a progressive number instead of the default value, it is useful for books.

## Advanced usage

All the functions have been defined in `iiif.py`, you can include it in your project and run more complicated tasks. Have a look at the example directory.
