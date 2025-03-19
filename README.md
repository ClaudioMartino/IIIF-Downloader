# Download all the images from an IIIF manifest

IIIF is the [International Image Interoperability Framework](https://iiif.io/), a set of open standards for digital objects online.

Most of the Python scripts out there ask you to install plenty of heavy external libraries. This script needs only standard libraries!

It works with the [2.0 API](https://iiif.io/api/presentation/2.0) and the [3.0 API](https://iiif.io/api/presentation/3.0) (beta version).

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

## Working manifests
The script has been tested with the following 2.0 manifests and it worked:
- https://api.irht.cnrs.fr/ark:/63955/fl685opg22dv/manifest.json
- https://content.staatsbibliothek-berlin.de/dc/785884734/manifest
- https://mss-cat.trin.cam.ac.uk/Manuscript/R.15.32/manifest.json
- https://digitallibrary.unicatt.it/veneranda/data/public/manifests/0b/02/da/82/80/0a/f4/58/0b02da82800af458.json
- https://www.e-rara.ch/i3f/v20/14575305/manifest
- https://acs.jarvis.memooria.org/meta/iiif/bdd8df6f-dc05-431c-955a-be2078018553/manifest
- https://adore.ugent.be/IIIF/manifests/archive.ugent.be%3A4B39C8CA-6FF9-11E1-8C42-C8A93B7C8C91
- https://d.lib.ncsu.edu/collections/catalog/nubian-message-1992-11-30/manifest
- https://iiif.bodleian.ox.ac.uk/iiif/manifest/60834383-7146-41ab-bfe1-48ee97bc04be.json
- https://digital.library.villanova.edu/Item/vudl:92879/Manifest 

Also with these 2.0 collections:
- https://iiif.wellcomecollection.org/presentation/v2/b20417081
- https://images.lambethpalacelibrary.org.uk/luna/servlet/iiif/collection/s/y4pi93

And with these 3.0 manifests:
- https://iiif.io/api/cookbook/recipe/0001-mvm-image/manifest.json
- https://iiif.io/api/cookbook/recipe/0004-canvas-size/manifest.json
- https://iiif.io/api/cookbook/recipe/0005-image-service/manifest.json
- https://iiif.io/api/cookbook/recipe/0009-book-1/manifest.json

And with this 3.0 collection:
- https://iiif.io/api/cookbook/recipe/0032-collection/collection.json
