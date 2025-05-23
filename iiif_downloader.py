"""Download all images from an IIIF manifest."""

import logging
from re import match, Match
import argparse
import json
import time
import os
from shutil import rmtree
from urllib.request import urlopen, Request
from urllib.error import URLError
from typing import List, Tuple, Dict, Any
from ssl import create_default_context, CERT_NONE

issue_str = "\nPLEASE submit a bug report to \
https://github.com/ClaudioMartino/IIIF-Downloader/issues \
and include the manifest"


class Conf:
    """A class containing all user configurations."""
    def __init__(self, firstpage: int = 1, lastpage: int = -1,
                 force: bool = False, use_labels: bool = False,
                 all_images: bool = False, width: int | None = 0):
        self.firstpage = firstpage
        self.lastpage = lastpage
        self.force = force
        self.use_labels = use_labels
        self.all_images = all_images
        # width = 0 (default) when -w is not used; = None for -w without arg
        self.width = width


class Info:
    """A class containing the features of an IIIF file."""
    def __init__(self, label: str = "NA", iiif_id: List[str] = [],
                 ext: List[str] = [], iiif_w: int = 0, iiif_h: int = 0,
                 service_id: List[str | None] = []):
        self.label = label
        self.id = iiif_id
        self.ext = ext
        self.w = iiif_w
        self.h = iiif_h
        self.service_id = service_id


def print_statistics(downloaded_cnt: int, total_time: float,
                     total_filesize: int) -> None:
    """Print useful statistics."""
    logging.info("--- Stats ---")
    logging.info("- Downloaded files: " + str(downloaded_cnt))
    logging.info("- Elapsed time: " + str(round(total_time)) + " s")
    if (downloaded_cnt > 0):
        logging.info(
            "- Avg time/file: " + str(round(total_time / downloaded_cnt)) +
            " s")
        logging.info(
            "- Disc usage: " + str(round(total_filesize / 1000)) + " kB")
        logging.info(
            "- Avg file size: " +
            str(round(total_filesize / (downloaded_cnt * 1000))) + " kB")
    logging.info("-------------")


def open_url(url: str, timeout: int = 30):
    """Open url."""
    # Create url request
    headers = {"User-Agent": "Mozilla/5.0"}
    url_req = Request(url, headers=headers)

    # Create default SSL context
    ctx = create_default_context()

    # Open the url
    try:
        response = urlopen(url_req, timeout=timeout, context=ctx)
        return response
    except Exception as e:
        logging.warning("Exception: " + str(e))

        # If the SSL certificate verification fails, try disabling it
        if isinstance(e, URLError):
            if "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
                logging.debug("Disabling SSL certificate verification")
                ctx.check_hostname = False
                ctx.verify_mode = CERT_NONE
                try:
                    response = urlopen(url_req, timeout=timeout, context=ctx)
                    return response
                except Exception as e:
                    logging.warning("Exception: " + str(e))
                    return None
        else:
            return None


def download_file(url: str, filepath: str) -> int:
    """Open a connection to a remote file and save it locally."""
    url = url.replace(" ", "%20")
    logging.debug("Downloading " + url + "...")

    # Open connection to remote file
    res = open_url(url)
    if (res is None):
        return -1
    else:
        logging.debug("HTTP status code: " + str(res.getcode()))

    # file_size = res.headers["Content-Length"]

    # Create the file (binary mode) even when it exists
    with open(filepath, "wb") as file:
        try:
            file.write(res.read())
            # Flush the write buffer to ensure that its content is dumped to
            # the file before calling getsize
            file.flush()
            file_size = os.path.getsize(filepath)
            return file_size
        except Exception as e:
            logging.warning("Exception: " + str(e))
            os.remove(filepath)
            return -1


def is_url(url: str) -> bool:
    """Check if string is an URL."""
    return (url[:4] == "http")


def get_extension(mime_type: str, file_id: str, nc: int) -> str:
    """Return the extension given the MIME type (IIIF format)."""
    # Take the extension from the format
    mime_to_extension = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",  # 'image/jpg' is wrong, nevertheless it is used
        "image/tiff": ".tif",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/jp2": ".jp2",
        "application/pdf": ".pdf",
        "image/webp": ".webp"
    }
    ext = mime_to_extension.get(mime_type, "NA")
    if (ext == "NA"):
        logging.debug(
            "File extension of canvas " + str(nc) +
            " is not correctly defined")

    # Try to take the extension from the file name
    if ("/default." in file_id):
        ext_from_id = "." + file_id.split(".")[-1]
        if (ext != ext_from_id):
            if (ext == "NA"):
                logging.debug(
                    "File extension of canvas " + str(nc) +
                    " extracted from file ID ('" + ext_from_id + "')")
            else:
                logging.debug(
                    "File ID of canvas " + str(nc) +
                    " defines an extension ('" + ext_from_id +
                    "') different from the format defined one ('" + mime_type +
                    "' => '" + ext + "'). '" + ext_from_id +
                    "' has been taken into account")
            ext = ext_from_id

    return ext


def get_default_img_uri(base: str, size: str, extension: str) -> str:
    """Return a default image URI given base, size, and extension."""
    # URI: base/region/size/rotation/quality.extension
    # with region = 'full', rotation = '0', and quality = 'default'
    return base + "/full/" + size + "/0/default" + extension


def match_uri_pattern(uri: str) -> Match | None:
    """Check if a string conforms to the URI template."""
    # "The URI for requesting image information must conform to the following
    # URI template: {scheme}://{server}{/prefix}/{identifier}/{region}/{size}/
    # {rotation}/{quality}.{format}"
    # "The base URI is the URI up to the identifier, but not including the
    # trailing slash character or any of the subsequent parameters."
    pattern = r"(?P<base>.*)\/(?P<region>[a-zA-Z0-9,:.]+)\/" \
        r"(?P<size>[a-zA-Z0-9,!^:]+)\/(?P<rotation>[0-9!.]+)\/" \
        r"(?P<quality>[a-zA-Z]+)\.(?P<format>[a-zA-Z0-9]+)$"
    return match(pattern, uri)


def sanitize_name(title: str) -> str:
    """Sanitize file name in order to avoid errors."""
    max_len = 100
    title = title.replace("/", " ")
    title = title.replace(":", "")
    return title[:max_len]


def first_value(d: Dict) -> Any:
    """Return first value of a dictionary."""
    return next(iter(d.values()))


def debug_check(name: str, to_check: str, expected: str | None = None) -> None:
    """Check if a value has been found or compare it with the expected one."""
    if expected is None:
        if (to_check is None or to_check == "NA"):
            logging.debug(name.capitalize() + " not found")
    else:
        if (to_check != expected):
            logging.debug(
                "Unexpected " + name + " value: " + str(to_check) +
                " instead of " + str(expected))


def sanitize_label(label: Any, source: str) -> str:
    """Sanitize manifest or canvas labels in 2.0 manifests."""
    if (not isinstance(label, str)):
        logging.debug(
            source.capitalize() + " label is not a string: " + str(label))

    if (isinstance(label, list)):
        label = label[0]

    # "Language may be associated with strings that are intended to be
    # displayed to the user with the following pattern of @value plus the RFC
    # 5646 code in @language, instead of a plain string. This pattern may be
    # used in label"
    if (isinstance(label, Dict)):
        label = str(label.get("@value"))
        logging.debug(
            "Taking just the first '@value' of " + source + " label")

    return str(label)


def read_iiif_manifest2(d: Dict) -> Tuple[str, str, List[Info]]:
    """Download all the files from a 2.0 manifest."""
    # - label
    # - @id
    # - sequences:
    #   - canvases:
    #     - label
    #     - width
    #     - height
    #     - images (content):
    #       - resource:
    #         - @id
    #         - format
    #         - service:
    #           - @id

    # Read manifest label
    manifest_label = d.get("label", "NA")
    # "A manifest must have a label"
    debug_check("manifest label ('label')", manifest_label)
    manifest_label = sanitize_label(manifest_label, "manifest")

    # Read manifest ID
    manifest_id = d.get("@id", "NA")
    # "A manifest must have an id"
    debug_check("manifest ID ('@id')", manifest_id)

    # Read first sequence
    sequences = d.get("sequences")
    # "Each manifest must, and is very likely to, have one sequence"
    assert sequences is not None, \
        "Manifest sequences ('sequences') not found" + issue_str
    # [Assumption] One sequence in sequences ("very likely")
    if (len(sequences) > 1):
        logging.debug(
            "There are " + str(len(sequences)) +
            " sequences in the manifest, but only the first is read")
    sequence = sequences[0]
    debug_check("sequence type", sequence.get("@type"), "sc:Sequence")

    # Read all canvases
    canvases = sequence.get("canvases")
    # "Each sequence must have at least one canvas"
    assert canvases is not None, \
        "Canvases ('canvases') not found" + issue_str
    infos = []
    for nc, c in enumerate(canvases):
        debug_check("canvas type", c.get("@type"), "sc:Canvas")

        # "A canvas must have an id"
        debug_check("canvas ID", c.get("@id"))

        # Create an empty info node
        i = Info()

        # Read label, width and height
        label = c.get("label")
        iiif_w = c.get("width")
        iiif_h = c.get("height")
        # "Every canvas must have a label to display, and a height and a
        # width as integers"
        debug_check("canvas label", label)
        debug_check("canvas width", iiif_w)
        debug_check("canvas height", iiif_h)
        i.label = sanitize_label(label, "canvas " + str(nc))
        i.w = iiif_w
        i.h = iiif_h

        # Read images
        images = c.get("images")
        if (images):
            if (len(images) > 1):
                logging.debug(
                    "There are " + str(len(images)) + " images in canvas " +
                    str(nc))

            id_list = []
            ext_list = []
            service_id_list = []
            for img in images:
                # "All resources must have a type specified [...] Association
                # of images with their respective canvases is done via
                # annotations"
                debug_check("image type", img.get("@type"), "oa:Annotation")
                # "Each association of a content resource must have the
                # motivation field and the value must be “sc:painting”"
                debug_check(
                    "image motivation", img.get("motivation"), "sc:painting")

                resource = img.get("resource")
                # If resource has multiple images (choice), take just default
                if (resource.get("@type") == "oa:Choice"):
                    resource = resource.get("default")
                    logging.debug(
                        "The image in canvas " + str(nc) + " has multiple \
choices, but only the default one is read")

                iiif_id = resource.get("@id")
                # "The image must have an @id field"
                assert iiif_id is not None, \
                    "Image ID ('@id') not found" + issue_str

                iiif_format = resource.get("format")
                ext = get_extension(iiif_format, iiif_id, nc)

                service = resource.get("service")
                if (service is not None):
                    service_id = service.get("@id")
                else:
                    service_id = None

                id_list.append(iiif_id)
                ext_list.append(ext)
                service_id_list.append(service_id)

            i.id = id_list
            i.ext = ext_list
            i.service_id = service_id_list

        # Append info to info list
        infos.append(i)

    return manifest_label, manifest_id, infos


def read_iiif_manifest3(d: Dict) -> Tuple[str, str, List[Info]]:
    """Download all the files from a 3.0 manifest."""
    # - label
    # - id
    # - items (type: Canvas):
    #   - label
    #   - items (type: AnnotationPage):
    #     - items (type: Annotation):
    #       - body:
    #         - id
    #         - format
    #         - width
    #         - height
    #         - service:
    #           - @id

    # Read manifest label
    manifest_label = d.get("label", "NA")
    # "A Manifest must have the label property with at least one entry"
    debug_check("Manifest label ('label')", manifest_label)
    if (manifest_label != "NA"):
        # "The value of the property [label] must be a JSON object"
        assert isinstance(manifest_label, dict), \
            "Manifest label is not a JSON object" + issue_str
        manifest_label = first_value(manifest_label)  # Take first value
        manifest_label = str(manifest_label[0])

    # Read manifest ID
    manifest_id = d.get("id", "NA")
    debug_check("Manifest ID ('id')", manifest_id)

    # Read canvases
    canvases: Any = d.get("items")
    # "A Manifest must have the items property with at least one item"
    assert canvases is not None, \
        "Manifest canvases ('items') not found" + issue_str
    infos = []
    for nc, c in enumerate(canvases):
        debug_check("canvas type", c.get("type"), "Canvas")

        # "Canvases must be identified by a URI"
        debug_check("canvas ID", c.get("id"))

        # Create empty info node
        i = Info()

        # Read canvas label
        label = c.get("label", "NA")
        if (label != "NA"):
            # "A Canvas should have the label property [...] The value must be
            # a JSON object"
            assert isinstance(label, dict), \
                "Canvas label is not a JSON object" + issue_str
            label = first_value(label)  # Take first value
            label = str(label[0])
        i.label = label

        # "A Canvas must have a rectangular aspect ratio"
        debug_check("canvas height", c.get("height"))
        debug_check("canvas width", c.get("width"))

        # Read annotation page
        annotation_page = c.get("items")
        # "A Canvas should have the items property with at least one item. Each
        # item must be an Annotation Page"
        debug_check("annotation page ('items')", annotation_page)
        if (annotation_page):
            # [Assumption #1] One annotation page in canvas
            if (len(annotation_page) > 1):
                logging.debug(
                    "There are " + str(len(annotation_page)) +
                    " annotation pages in canvas " + str(nc) +
                    ", but only the first one is read")
            annotation_page = annotation_page[0]
            debug_check(
                "annotation page type", annotation_page.get("type"),
                "AnnotationPage")

            # "Annotation Pages must have the id"
            debug_check("annotation page ID", annotation_page.get("id"))

            # Read annotation
            annotation = annotation_page.get("items")
            # "An Annotation Page should have the items property with at
            # least one item. Each item must be an Annotation"
            debug_check("annotation ('items')", annotation)
            if (annotation):
                # [Assumption #2] One annotation in annotation page
                if (len(annotation) > 1):
                    logging.debug(
                        "There are " + str(len(annotation)) +
                        " annotation in the annotation page of canvas " +
                        str(nc) + ", but only the first one is read")
                annotation = annotation[0]
                debug_check(
                    "annotation type", annotation.get("type"), "Annotation")

                # "Annotations must have their own HTTP(S) URIs, conveyed
                # in the id property"
                debug_check("annotation ID", annotation.get("id"))
                # Content [...] must be associated by an Annotation that has
                # the motivation value painting"
                debug_check(
                    "annotation motivation", annotation.get("motivation"),
                    "painting")

                # Read body or body.source for "specific resources"
                body = annotation.get("body")
                body_type = body.get("type")
                if (body_type == "Image"):
                    source = body
                elif (body_type == "SpecificResource"):
                    source = body.get("source")
                else:
                    raise Exception(
                        "Unsupported body type: " + body_type + issue_str)

                # Read image ID, extension, dimensions and service ID
                iiif_id = source.get("id")
                i.id = [iiif_id]
                iiif_format = source.get("format")
                i.ext = [get_extension(iiif_format, iiif_id, nc)]
                iiif_w = source.get("width")
                i.w = iiif_w
                iiif_h = source.get("height")
                i.h = iiif_h
                service = source.get("service")
                if (service is not None):
                    if (isinstance(service, list)):
                        service = service[0]
                    i.service_id = [service.get("@id")]
                else:
                    i.service_id = [None]

        # Append info to list
        infos.append(i)

    return manifest_label, manifest_id, infos


def download_iiif_files_from_manifest(version: int, d: Dict, maindir: str,
                                      conf: Conf = Conf()) -> None:
    """Download all the files from a manifest."""
    # Parse manifest
    if (version == 2):
        manifest_label, manifest_id, infos = read_iiif_manifest2(d)
    elif (version == 3):
        manifest_label, manifest_id, infos = read_iiif_manifest3(d)
    else:
        raise Exception("Unsupported IIIF version ('" + str(version) + "')")

    # Print manifest features
    logging.debug("IIIF version: " + str(version) + ".0")
    logging.debug("Manifest ID: " + manifest_id)
    logging.info("Document title: " + manifest_label)
    logging.debug("Pages: " + str(len(infos)))

    if (infos):
        # Create subdirectory from manifest label
        manifest_label = sanitize_name(manifest_label)
        subdir = maindir + "/" + manifest_label
        if (not os.path.exists(subdir)):
            os.mkdir(subdir)
            logging.debug(manifest_label + " created in " + maindir)

        # Create image sub-list (conf.firstpage, conf.lastpage)
        totpages = len(infos)
        if (conf.firstpage != 1 or conf.lastpage != -1):
            infos = infos[conf.firstpage - 1:conf.lastpage]
            logging.info(
                "Downloading pages " + str(conf.firstpage) + "-"
                + str(conf.lastpage) + " from a total of " + str(totpages))

        # Set up the default priority flags (size = full not in the 3.0 API).
        # These flags correspond to different download strategies:
        # 1. If the service ID is defined in the manifest, try to download the
        # formatted URI with service ID as base and size = "full" (1a),
        # size = "max" (1b), or size = "width," (1c).
        if (version == 2):
            uri_base_serv_id_full = True
        else:
            uri_base_serv_id_full = False
        uri_base_serv_id_max = True
        uri_base_serv_id_width = True
        # 2. Try to download the image ID as it is written in the manifest, it
        # may be a formatted URI or another type of URI.
        uri_img_id = True
        # 3. If the image ID is a formatted URI, try to download it with size
        # changed to "full" (3a), "max" (3b), or "width," (3c).
        if (version == 2):
            uri_base_b_img_id_full = True
        else:
            uri_base_b_img_id_full = False
        uri_base_b_img_id_max = True
        uri_base_b_img_id_width = True
        # 4. Lastly, only if the image ID is not the service ID, try to
        # download the formatted URI with image ID as base and size = "full"
        # (4a), size = "max" (4b), or size = "width," (4c).
        if (version == 2):
            uri_base_img_id_full = True
        else:
            uri_base_img_id_full = False
        uri_base_img_id_max = True
        uri_base_img_id_width = True

        # Unset all flags except width-related ones if '-w' has been set
        if (conf.width != 0):
            uri_base_serv_id_full = uri_base_serv_id_max = uri_img_id = \
                uri_base_b_img_id_full = uri_base_b_img_id_max = \
                uri_base_img_id_full = uri_base_img_id_max = False

        # Loop over each document page
        some_error = False
        total_filesize = 0
        downloaded_cnt = 0
        start_time = time.time()
        for cnt, info in enumerate(infos):
            # Print counters and label
            percentage = round((cnt + 1) / len(infos) * 100, 1)
            logging.info(
                "[n." + str(cnt + conf.firstpage) + "/" + str(totpages) + "; "
                + str(percentage) + "%] Label: " + info.label)

            # Change the width if the user defined a new one with '-w'
            if (isinstance(conf.width, int) and conf.width != 0):
                if (isinstance(info.w, int) and isinstance(info.h, int)):
                    info.h = round(conf.width / info.w * info.h)
                logging.debug(
                    "Width is changed from " + str(info.w) + " px to " +
                    str(conf.width) + " px")
                info.w = conf.width

            # Print file dimensions
            logging.debug("Width: " + str(info.w) + " px")
            logging.debug("Height: " + str(info.h) + " px")

            # Check if one image ID (or more) was defined in the manifest
            if (len(info.id) == 0):
                logging.info("File not available in the manifest")
                continue

            # Take just the first file when '--all-images' is not set
            if (len(info.id) > 1 and not conf.all_images):
                logging.debug(
                    "There are " + str(len(info.id)) +
                    " images for this page, but only the first one is \
downloaded. Use the --all-images option to download everything")
                info.id = [info.id[0]]

            # Loop over each image ID (usually one iteration)
            for n, i in enumerate(info.id):
                # Print IDs and file extension
                logging.debug("Image ID: " + i)
                service_id = info.service_id[n]
                if (service_id is not None):
                    logging.debug("Service ID: " + service_id)
                ext = info.ext[n]
                logging.debug("Extension: " + ext)

                # Create output file name
                if (conf.use_labels):
                    filename = sanitize_name(info.label)
                else:
                    filename = "p" + str(cnt + conf.firstpage).zfill(3)
                if (len(info.id) > 1):
                    filename += "_" + str(n + 1)
                filename += ext
                logging.debug("Output file name: " + filename)
                subdir_filename = subdir + "/" + filename

                # Skip download if the file exists
                if (os.path.exists(subdir_filename) and not conf.force):
                    logging.info(
                        subdir_filename +
                        " exists, skip. Use the -f option to force overwrite.")
                    continue

                # Download the file.
                filesize = -1
                uri_base_serv_id = uri_base_serv_id_full or \
                    uri_base_serv_id_max or uri_base_serv_id_width
                # Check if a service ID has been defined in the manifest
                if (service_id is not None and uri_base_serv_id):
                    # 1a. formatted URI, base = service ID, size = full
                    if (uri_base_serv_id_full):
                        img_uri = get_default_img_uri(service_id, "full", ext)
                        filesize = download_file(img_uri, subdir_filename)
                        if (filesize <= 0):
                            logging.debug("Cannot download " + img_uri)
                            if (cnt == 0):
                                uri_base_serv_id_full = False

                    # 1b. formatted URI, base = service ID, size = max
                    if (uri_base_serv_id_max and filesize <= 0):
                        img_uri = get_default_img_uri(service_id, "max", ext)
                        filesize = download_file(img_uri, subdir_filename)
                        if (filesize <= 0):
                            logging.debug("Cannot download " + img_uri)
                            if (cnt == 0):
                                uri_base_serv_id_max = False

                    # 1c. formatted URI, base = service ID, size = width,
                    if (uri_base_serv_id_width and filesize <= 0):
                        img_uri = get_default_img_uri(
                            service_id, str(info.w) + ",", ext)
                        filesize = download_file(img_uri, subdir_filename)
                        if (filesize <= 0):
                            logging.debug("Cannot download " + img_uri)
                            if (cnt == 0):
                                uri_base_serv_id_width = False

                # 2. Image ID as it is
                if (uri_img_id and filesize <= 0):
                    filesize = download_file(i, subdir_filename)
                    if (filesize <= 0):
                        logging.debug("Cannot download " + i)
                        if (cnt == 0):
                            uri_img_id = False

                uri_base_b_img_id = uri_base_b_img_id_full or \
                    uri_base_b_img_id_max or uri_base_b_img_id_width
                # Check if the image ID is formatted as the URI pattern
                regex_match_id = match_uri_pattern(i)
                if (regex_match_id is not None and uri_base_b_img_id):
                    id_base = regex_match_id.group("base")
                    if (service_id != id_base):
                        # 3a. Image ID (formatted URI), size changed to full
                        if (uri_base_b_img_id_full and filesize <= 0):
                            img_uri = get_default_img_uri(id_base, "full", ext)
                            filesize = download_file(img_uri, subdir_filename)
                            if (filesize <= 0):
                                logging.debug("Cannot download " + img_uri)
                                if (cnt == 0):
                                    uri_base_b_img_id_full = False

                        # 3b. Image ID (formatted URI), size changed to max
                        if (uri_base_b_img_id_max and filesize <= 0):
                            img_uri = get_default_img_uri(id_base, "max", ext)
                            filesize = download_file(img_uri, subdir_filename)
                            if (filesize <= 0):
                                logging.debug("Cannot download " + img_uri)
                                if (cnt == 0):
                                    uri_base_b_img_id_max = False

                        # 3c. Image ID (formatted URI), size changed to width,
                        if (uri_base_b_img_id_width and filesize <= 0):
                            img_uri = get_default_img_uri(
                                id_base, str(info.w) + ",", ext)
                            filesize = download_file(img_uri, subdir_filename)
                            if (filesize <= 0):
                                logging.debug("Cannot download " + img_uri)
                                if (cnt == 0):
                                    uri_base_b_img_id_width = False

                uri_base_img_id = uri_base_img_id_full or uri_base_img_id_max \
                    or uri_base_img_id_width
                # Check if the image ID is different from the service ID
                if (i != service_id and uri_base_img_id):
                    # 4a. formatted URI, base = image ID, size = full
                    if (uri_base_img_id_full and filesize <= 0):
                        img_uri = get_default_img_uri(i, "full", ext)
                        filesize = download_file(img_uri, subdir_filename)
                        if (filesize <= 0):
                            logging.debug("Cannot download " + img_uri)
                            if (cnt == 0):
                                uri_base_img_id_full = False

                    # 4b. formatted URI, base = image ID, size = max
                    if (uri_base_img_id_max and filesize <= 0):
                        img_uri = get_default_img_uri(i, "max", ext)
                        filesize = download_file(img_uri, subdir_filename)
                        if (filesize <= 0):
                            logging.debug("Cannot download " + img_uri)
                            if (cnt == 0):
                                uri_base_img_id_max = False

                    # 4c. formatted URI, base = image ID, size = width,
                    if (filesize <= 0):
                        img_uri = get_default_img_uri(
                            i, str(info.w) + ",", ext)
                        filesize = download_file(img_uri, subdir_filename)
                        if (filesize <= 0):
                            logging.debug("Cannot download " + img_uri)
                            if (cnt == 0):
                                uri_base_img_id_width = False

                # Print final message and update counters
                if (filesize <= 0):
                    logging.error(
                        "\033[91mCannot download page n." +
                        str(cnt + conf.firstpage) + "\033[0m")
                    some_error = True
                else:
                    logging.info(
                        "\033[92m" + filename + " (" +
                        str(round(filesize / 1000)) + " kB) saved in " +
                        subdir + "\033[0m")
                    total_filesize += filesize
                    downloaded_cnt = downloaded_cnt + 1

        # Print some statistics
        total_time = time.time() - start_time
        print_statistics(downloaded_cnt, total_time, total_filesize)

        # Rename the directory if something was wrong
        if (some_error):
            err_subdir = maindir + "/" + "ERR_" + manifest_label
            if os.path.exists(err_subdir):
                rmtree(err_subdir)
            os.rename(subdir, err_subdir)
            logging.error(
                "\033[91m" + "Some error with " + manifest_label + "\033[0m")


def download_iiif_files_from_collection(version: int, d: Dict, maindir: str,
                                        conf: Conf = Conf()) -> None:
    """Download all the files from a collection of manifests."""
    if (version == 2):
        manifests_key = "manifests"
        id_key = "@id"
    else:
        manifests_key = "items"
        id_key = "id"

    manifests = d.get(manifests_key)
    if (manifests):
        logging.info(
            str(len(manifests)) + " manifests found in the collection")
        for m in manifests:
            manifest_id = m.get(id_key)
            d = json.loads(open_url(manifest_id).read())
            download_iiif_files_from_manifest(version, d, maindir, conf)
    else:
        raise Exception(
            "Cannot find manifests ('" + manifests_key + "') in collection")


def get_iiif_version(d: Dict) -> int:
    """ Check IIIF version from a manifest or a collection."""
    # Get context
    context = d.get("@context")

    # 3.0 API: "The value of the @context property must be either the URI or a
    # JSON array with the URI as the last item"
    if (isinstance(context, list)):
        context = context[-1]

    if (context.endswith("2/context.json")):
        version = 2
    elif (context.endswith("3/context.json")):
        version = 3
    else:
        # "The top level resource must have the @context property"
        raise Exception(
            "Unsupported IIIF version (context: " + context + ")")

    return version


def open_json_file(json_file: str) -> Dict:
    """Check if json file is local or remote and read it."""
    if (is_url(json_file)):
        response = open_url(json_file)
        if (response is not None):
            d = json.loads(response.read())
        else:
            raise Exception("Cannot read remote manifest " + json_file)
    else:
        if (os.path.isfile(json_file)):
            with open(json_file) as f:
                d = json.load(f)
        else:
            raise Exception("Cannot open manifest " + json_file)

    return d


def download_iiif_files(json_file: str, maindir: str,
                        conf: Conf = Conf()) -> None:
    """Download all the files from a manifest or a collection."""
    # Open json file
    d = open_json_file(json_file)

    # Check IIIF version
    version = get_iiif_version(d)

    # Check if the input file is a manifest or a collection
    if (version == 2):
        type_key = "@type"
        type_val_manifest = "sc:Manifest"
        type_val_collection = "sc:Collection"
    else:
        type_key = "type"
        type_val_manifest = "Manifest"
        type_val_collection = "Collection"

    iiif_type = str(d.get(type_key))
    if (iiif_type.lower() == type_val_manifest.lower()):
        download_iiif_files_from_manifest(version, d, maindir, conf)
    elif (iiif_type.lower() == type_val_collection.lower()):
        # TODO: one directory for the same collection?
        download_iiif_files_from_collection(version, d, maindir, conf)
    else:
        raise Exception(
            "Not a manifest or a collection of manifests (type: '"
            + str(iiif_type) + "')")


def get_pages(pages: str) -> Tuple[int, int]:
    """Return the first and the last page as integers given one string."""
    if (pages != "all"):
        # Two positive numbers separated by -
        pattern = r"^(?!0-0)([1-9]\d*)-([1-9]\d*)$"
        if (match(pattern, pages)):
            firstpage, lastpage = map(int, pages.split("-"))
            if (lastpage < firstpage):
                raise Exception("Invalid page range (invalid pages)")
        else:
            raise Exception("Invalid page range (invalid format)")
    else:
        firstpage, lastpage = 1, -1

    return firstpage, lastpage


def set_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)

    general = parser.add_argument_group("General options")
    general.add_argument(
        "-m", metavar="<file>", required=True,
        help="Manifest or collection of manifests (local file or url)")
    general.add_argument(
        "-d", metavar="<path>", default=".",
        help="Output directory")
    general.add_argument(
        "-p", metavar="<first>-<last>", default="all",
        help="Range of pages to download")
    general.add_argument(
        "-w", nargs="?", metavar="<width>", default=0, type=int,
        help="Width of the images; without argument for the width defined in \
the manifest")
    general.add_argument(
        "-f", "--force", action="store_true",
        help="Overwrite existing files")
    general.add_argument(
        "--use-labels", action="store_true",
        help="Name the downloaded files with their labels")
    general.add_argument(
        "--all-images", action="store_true",
        help="Download all the images related to the same page in 2.0/2.1 \
manifests, not just the first one")
    general.add_argument(
        "-h", "--help", action="help",
        help="Print this help message and exit")

    output = parser.add_argument_group("Output options")
    output.add_argument(
        "-v", "--verbose", default=logging.INFO, action="store_const",
        dest="logging_level", const=logging.DEBUG,
        help="Print more information about what is happening")
    output.add_argument(
        "-q", "--quiet", default=logging.INFO, action="store_const",
        dest="logging_level", const=logging.ERROR,
        help="Activate quiet mode and print only error messages")

    return parser


if __name__ == "__main__":
    # Configure parser for user defined command line options
    parser = set_parser()
    config = vars(parser.parse_args())

    # Configure logger with user defined logging level
    logging.basicConfig(level=config["logging_level"], format="%(message)s")

    # Create configuration structure
    firstpage, lastpage = get_pages(config["p"])
    conf = Conf(firstpage, lastpage, config["force"], config["use_labels"],
                config["all_images"], config["w"])

    # Call main function
    download_iiif_files(config["m"], config["d"], conf)
