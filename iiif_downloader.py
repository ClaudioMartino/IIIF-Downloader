"""Download all images from an IIIF manifest."""

import logging
from re import match
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
and include the manifest."


class Conf:
    """A class containing all user configurations."""
    def __init__(self, firstpage: int = 1, lastpage: int = -1,
                 force: bool = False, use_labels: bool = False,
                 all_images: bool = False):
        self.firstpage = firstpage
        self.lastpage = lastpage
        self.force = force
        self.use_labels = use_labels
        self.all_images = all_images


class Info:
    """A class containing the features of an IIIF file."""
    def __init__(self, label: str = "NA", iiif_id: List[str] = [],
                 iiif_format: List[str] = [], iiif_w: int = 0,
                 iiif_h: int = 0):
        self.label = label
        self.id = iiif_id
        self.format = iiif_format
        self.w = iiif_w
        self.h = iiif_h


def print_statistics(downloaded_cnt: int, total_time: float,
                     total_filesize: int) -> None:
    """Print useful statistics."""
    logging.info("--- Stats ---")
    logging.info("- Downloaded files: " + str(downloaded_cnt))
    logging.info("- Elapsed time: " + str(round(total_time)) + " s")
    if (downloaded_cnt > 0):
        logging.info(
            "- Avg time/file: "
            + str(round(total_time / downloaded_cnt)) + " s")
        logging.info(
            "- Disc usage: " + str(round(total_filesize / 1000)) + " kB")
        logging.info(
            "- Avg file size: "
            + str(round(total_filesize / (downloaded_cnt * 1000))) + " kB")
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
        logging.debug("- Exception: " + str(e))

        # If SSL certificate verification fails, try disabling it
        if isinstance(e, URLError):
            if 'CERTIFICATE_VERIFY_FAILED' in str(e.reason):
                logging.debug("- Disabling SSL certificate verification")
                ctx.check_hostname = False
                ctx.verify_mode = CERT_NONE
                try:
                    response = urlopen(url_req, timeout=timeout, context=ctx)
                    return response
                except Exception as e:
                    logging.debug("- Exception: " + str(e))
                    return None
        else:
            return None


def download_file(url: str, filepath: str) -> int:
    """Open a remote file and save it locally."""
    url = url.replace(" ", "%20")
    logging.debug("- Downloading " + url + "...")

    # Open connection to remote file
    res = open_url(url)
    if (res is None):
        return -1
    else:
        logging.debug("- HTTP status code: " + str(res.getcode()))

    # file_size = res.headers['Content-Length']

    # Create the file (binary mode) even when it exists
    with open(filepath, 'wb') as file:
        try:
            file.write(res.read())
            file_size = os.path.getsize(filepath)
            return file_size
        except Exception as err:
            logging.error(err)
            os.remove(filepath)
            return -1


def is_url(url: str) -> bool:
    """Check if string is an URL."""
    return (url[:4] == 'http')


def get_extension(mime_type: str) -> str:
    """Return the extension given the MIME type (IIIF format)."""
    mime_to_extension = {
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',  # 'image/jpg' is wrong, nevertheless it is used
        'image/tiff': '.tif',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/jp2': '.jp2',
        'application/pdf': '.pdf',
        'image/webp': '.webp'
    }
    return mime_to_extension.get(mime_type, 'NA')


def get_img_url(iiif_id: str, ext: str, region: str = 'full',
                size: str = 'max', rotation: str = '0',
                quality: str = 'default') -> str:
    """Return image url given its parts."""
    return iiif_id + '/' + region + '/' + size + '/' + rotation + '/' + \
        quality + ext


def sanitize_name(title: str) -> str:
    """Sanitize file name in order to avoid errors."""
    title = title.replace("/", " ")
    title = title.replace(":", "")
    return title


def debug_check(name: str, to_check: str, expected: str | None = None) -> None:
    """Check if a value has been found or compare it with the expected one."""
    if expected is None:
        if (to_check is None or to_check == 'NA'):
            logging.debug("- " + name.capitalize() + " not found.")
    else:
        if (to_check != expected):
            logging.debug(
                "- Unexpected " + name + " value: " + str(to_check)
                + " instead of " + str(expected) + ".")


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

    # Read manifest label
    manifest_label = str(d.get('label', "NA"))
    # "A manifest must have a label"
    debug_check("manifest label ('label')", manifest_label)

    # Read manifest id
    manifest_id = d.get('@id', "NA")
    # "A manifest must have an id"
    debug_check("manifest id ('@id')", manifest_id)

    # Read first sequence
    sequences = d.get('sequences')
    # "Each manifest must, and is very likely to, have one sequence"
    assert sequences is not None, \
        "Manifest sequences ('sequences') not found." + issue_str
    # [Assumption] One sequence in sequences ("very likely")
    if (len(sequences) > 1):
        logging.debug(
            '- There are ' + str(len(sequences)) +
            ' sequences in the manifest, but only the first is read.')
    sequence = sequences[0]
    debug_check('sequence type', sequence.get('@type'), 'sc:Sequence')

    # Read all canvases
    canvases = sequence.get('canvases')
    # "Each sequence must have at least one canvas"
    assert canvases is not None, "Canvases not found. " + issue_str
    infos = []
    for nc, c in enumerate(canvases):
        debug_check('canvas type', c.get('@type'), 'sc:Canvas')

        # "A canvas must have an id"
        debug_check('canvas ID', c.get('@id'))

        # Create an empty info node
        i = Info()

        # Read label, width and height
        label = c.get('label')
        iiif_w = c.get('width')
        iiif_h = c.get('height')
        # "Every canvas must have a label to display, and a height and a
        # width as integers"
        debug_check('canvas label', label)
        debug_check('canvas width', iiif_w)
        debug_check('canvas height', iiif_h)
        i.label = label
        i.w = iiif_w
        i.h = iiif_h

        # Read images
        images = c.get("images")
        if (images):
            if (len(images) > 1):
                logging.debug(
                    '- There are ' + str(len(images)) + ' images in canvas ' +
                    str(nc) + '.')

            id_list = []
            format_list = []
            for img in images:
                # "All resources must have a type specified"
                debug_check('image type', img.get('@type'), 'oa:Annotation')
                # "Each association of a content resource must have the
                # motivation field and the value must be “sc:painting”
                debug_check(
                    'image motivation', img.get('motivation'), 'sc:painting')

                resource = img.get('resource')
                # If resource has multiple images (choice), take just default
                if (resource.get('@type') == 'oa:Choice'):
                    resource = resource.get('default')
                    logging.debug(
                        '- The image in canvas ' + str(nc) + ' has multiple \
choices, but only the default one is read.')

                iiif_id = resource.get('@id')
                # "The image must have an @id field"
                assert iiif_id is not None, \
                    "Image id ('@id') not found." + issue_str

                iiif_format = resource.get('format', 'NA')

                id_list.append(iiif_id)
                format_list.append(iiif_format)

            i.id = id_list
            i.format = format_list

        # Append info to list
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

    # Read manifest label
    manifest_label = d.get('label', "NA")
    # "A Manifest must have the label property with at least one entry"
    debug_check("Manifest label ('label')", manifest_label)
    if (manifest_label != "NA"):
        # "The value of the property [label] must be a JSON object"
        assert isinstance(manifest_label, dict), \
            "Manifest label is not a JSON object." + issue_str
        manifest_label = next(iter(manifest_label.values()))  # Take first val
        manifest_label = manifest_label[0]

    # Read manifest id
    manifest_id = d.get('id', "NA")
    debug_check("Manifest id ('id')", manifest_id)

    # Read canvases
    canvases: Any = d.get('items')
    # "A Manifest must have the items property with at least one item"
    assert canvases is not None, \
        "Manifest canvases ('items') not found." + issue_str
    infos = []
    for nc, c in enumerate(canvases):
        debug_check('canvas type', c.get('type'), 'Canvas')

        # "Canvases must be identified by a URI"
        debug_check('canvas id', c.get('id'))

        # Create empty info node
        i = Info()

        # Read canvas label
        label = c.get('label', 'NA')
        if (label != 'NA'):
            # "A Canvas should have the label property [...] The value must be
            # a JSON object"
            assert isinstance(label, dict), \
                "Canvas label is not a JSON object." + issue_str
            label = next(iter(label.values()))  # Take first value
            label = label[0]
        i.label = label

        # "A Canvas must have a rectangular aspect ratio"
        debug_check('canvas height', c.get('height'))
        debug_check('canvas width', c.get('width'))

        # Read annotation page
        annotation_page = c.get('items')
        # "A Canvas should have the items property with at least one item. Each
        # item must be an Annotation Page"
        debug_check("annotation page ('items')", annotation_page)
        if (annotation_page):
            # [Assumption #1] One annotation page in canvas
            if (len(annotation_page) > 1):
                logging.debug(
                    '- There are ' + str(len(annotation_page)) +
                    ' annotation pages in canvas ' + str(nc) +
                    ', but only the first one is read.')
            annotation_page = annotation_page[0]
            debug_check(
                "annotation page type", annotation_page.get('type'),
                'AnnotationPage')

            # "Annotation Pages must have the id"
            debug_check("annotation page id", annotation_page.get('id'))

            # Read annotation
            annotation = annotation_page.get('items')
            # "An Annotation Page should have the items property with at
            # least one item. Each item must be an Annotation"
            debug_check("annotation ('items')", annotation)
            if (annotation):
                # [Assumption #2] One annotation in annotation page
                if (len(annotation) > 1):
                    logging.debug(
                        '- There are ' + str(len(annotation)) +
                        ' annotation in the annotation page of canvas ' +
                        str(nc) + ', but only the first one is read.')
                annotation = annotation[0]
                debug_check(
                    'annotation type', annotation.get('type'), 'Annotation')

                # "Annotations must have their own HTTP(S) URIs, conveyed
                # in the id property"
                debug_check('annotation id', annotation.get('id'))
                # Content [...] must be associated by an Annotation that has
                # the motivation value painting"
                debug_check(
                    'annotation motivation', annotation.get('motivation'),
                    'painting')

                # Read body or body.source for "specific resources"
                body = annotation.get('body')
                body_type = body.get('type')
                if (body_type == 'Image'):
                    source = body
                elif (body_type == 'SpecificResource'):
                    source = body.get('source')
                else:
                    raise Exception(
                        "Unsupported body type: " + body_type + issue_str)

                # Read image id, format, and dimensions
                iiif_id = source.get('id')
                i.id = [iiif_id]
                iiif_format = source.get('format')
                i.format = [iiif_format]
                iiif_w = source.get('width')
                i.w = iiif_w
                iiif_h = source.get('height')
                i.h = iiif_h

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
        raise Exception("Unsupported IIIF version (" + str(version) + ")")

    # Print manifest features
    logging.debug('- IIIF version: ' + str(version) + '.0')
    logging.debug('- Manifest ID: ' + manifest_id)
    logging.info('- Document title: ' + manifest_label)
    logging.info('- Pages: ' + str(len(infos)))

    if (len(infos) > 0):
        # Create subdirectory from manifest label
        subdir = maindir + '/' + sanitize_name(manifest_label)
        if (not os.path.exists(subdir)):
            os.mkdir(subdir)
            logging.debug(
                '- ' + sanitize_name(manifest_label) + ' created in '
                + maindir)

        # Create image sub-list (conf.firstpage, conf.lastpage)
        totpages = len(infos)
        if (conf.firstpage != 1 or conf.lastpage != -1):
            infos = infos[conf.firstpage - 1:]
            infos = infos[:conf.lastpage - conf.firstpage + 1]
            logging.info(
                "- Downloading pages " + str(conf.firstpage) + "-"
                + str(conf.lastpage) + " from a total of " + str(totpages))

        # Loop over each page
        some_error = False
        try_with_id = True
        total_filesize = 0
        downloaded_cnt = 0
        start_time = time.time()
        for cnt, info in enumerate(infos):
            # Print counters and label
            percentage = round((cnt + 1) / len(infos) * 100, 1)
            cnt = cnt + conf.firstpage - 1
            logging.info(
                '[n.' + str(cnt + 1) + '/' + str(totpages) + '; '
                + str(percentage) + '%] Label: ' + info.label)

            # Print file dimensions
            logging.info('- Width: ' + str(info.w) + ' px')
            logging.info('- Height: ' + str(info.h) + ' px')

            # Take just the first file when 'all-images' is not set
            if (len(info.id) > 1 and not conf.all_images):
                logging.debug(
                    '- There are ' + str(len(info.id)) +
                    ' images for this page, but only the first one is \
downloaded. Use the --all-images option to download everything.')
                info.id = [info.id[0]]

            for n, i in enumerate(info.id):
                # Print file ID
                logging.info('- ID: ' + i)
                if (i == 'NA'):
                    logging.debug('- File not available in the manifest, skip')
                    continue

                # Print file format and extension
                logging.info('- Format: ' + info.format[n])
                ext = get_extension(info.format[n])
                # If the format has not been found in the manifest, try to take
                # the extension from the file name
                if (ext == 'NA' and '.' in i):
                    ext = '.' + i.split('.')[-1]
                logging.info('- Extension: ' + ext)

                # Create file name
                if (conf.use_labels):
                    filename = sanitize_name(info.label)
                else:
                    filename = 'p' + str(cnt + 1).zfill(3)
                if (len(info.id) > 1):
                    filename += '_' + str(n + 1)
                filename += ext
                subdir_filename = subdir + '/' + filename

                # Download file
                if (os.path.exists(subdir_filename) and not conf.force):
                    logging.debug(
                        '- ' + subdir_filename + ' exists, skip')
                    continue

                # Priority to the image id, but if it doesn't work, we move
                # to the URI template and we stop trying with the image id
                filesize = -1
                if (try_with_id):
                    filesize = download_file(i, subdir_filename)
                    if (filesize <= 0):
                        logging.debug("- Cannot download " + i)
                        try_with_id = False

                if (filesize <= 0):
                    img_url = get_img_url(i, ext)
                    filesize = download_file(img_url, subdir_filename)

                # Print final message and update counters
                if (filesize <= 0):
                    logging.error('\033[91m' + '- Error!' + '\033[0m')
                    some_error = True
                else:
                    logging.info(
                        '\033[92m' + '- ' + filename + ' ('
                        + str(round(filesize / 1000)) + ' kB) saved in '
                        + subdir + '.' + '\033[0m')
                    total_filesize += filesize
                    downloaded_cnt = downloaded_cnt + 1

        total_time = time.time() - start_time

        # Print some statistics
        print_statistics(downloaded_cnt, total_time, total_filesize)

        # Rename directory if something was wrong
        if (some_error):
            err_subdir = maindir + '/' + 'ERR_' + sanitize_name(manifest_label)
            if os.path.exists(err_subdir):
                rmtree(err_subdir)
            os.rename(subdir, err_subdir)
            logging.error(
                '\033[91m' + 'Some error with '
                + sanitize_name(manifest_label) + '.\033[0m')


def download_iiif_files_from_collection(version: int, d: Dict, maindir: str,
                                        conf: Conf = Conf()) -> None:
    """Download all the files from a collection of manifests."""
    if (version == 2):
        manifests_key = 'manifests'
        id_key = '@id'
    else:
        manifests_key = 'items'
        id_key = 'id'

    manifests = d.get(manifests_key)
    if (manifests):
        for m in manifests:
            manifest_id = m.get(id_key)
            d = json.loads(open_url(manifest_id).read())
            download_iiif_files_from_manifest(version, d, maindir, conf)
    else:
        raise Exception(
            "Cannot find manifests (" + manifests_key + ") in collection")


def get_iiif_version(d: Dict) -> int:
    """ Check IIIF version from a manifest or a collection."""
    # Get context
    context = d.get('@context')

    # 3.0 API: "The value of the @context property must be either the URI or a
    # JSON array with the URI as the last item"
    if (isinstance(context, list)):
        context = context[-1]

    if (context.endswith('2/context.json')):
        version = 2
    elif (context.endswith('3/context.json')):
        version = 3
    else:
        # "The top level resource must have the @context property"
        raise Exception("Unsupported IIIF version (context: " + context + ')')

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
        type_key = '@type'
        type_val_manifest = 'sc:Manifest'
        type_val_collection = 'sc:Collection'
    else:
        type_key = 'type'
        type_val_manifest = 'Manifest'
        type_val_collection = 'Collection'

    iiif_type = str(d.get(type_key))
    if (iiif_type.lower() == type_val_manifest.lower()):
        download_iiif_files_from_manifest(version, d, maindir, conf)
    elif (iiif_type.lower() == type_val_collection.lower()):
        # TODO: one directory for the same collection?
        download_iiif_files_from_collection(version, d, maindir, conf)
    else:
        raise Exception(
            "Not a manifest or a collection of manifests (type: "
            + str(iiif_type) + ")")


def get_pages(pages: str) -> Tuple[int, int]:
    """Return the first and the last page as integers given one string."""
    if (pages != 'all'):
        # Two positive numbers separated by -
        pattern = r'^(?!0-0)([1-9]\d*)-([1-9]\d*)$'
        if (match(pattern, pages)):
            firstpage, lastpage = map(int, pages.split('-'))
            if (lastpage < firstpage):
                raise Exception("Invalid page range (invalid pages)")
        else:
            raise Exception("Invalid page range (invalid format)")
    else:
        firstpage, lastpage = 1, -1

    return firstpage, lastpage


if __name__ == "__main__":
    # Parse user defined arguments
    parser = argparse.ArgumentParser(
        description="IIIF Downloader",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-v", "--verbose",
        action='store_true',
        help="print more information about what is happening")
    parser.add_argument(
        "-m", "--manifest",
        default='manifest',
        help="manifest or collection of manifests (local file name or url)")
    parser.add_argument(
        "-d", "--directory",
        default='.',
        help="target directory")
    parser.add_argument(
        "-p", "--pages",
        default='all',
        help="range of pages to download (e.g. 3-27)")
    parser.add_argument(
        "-f", "--force",
        action='store_true',
        help="overwrite existing files")
    parser.add_argument(
        "--use-labels",
        action='store_true',
        help="name the downloaded files with their labels")
    parser.add_argument(
        "--all-images",
        action='store_true',
        help="download all images related to the pages in 2.0 manifests, not \
just the first one")

    config = vars(parser.parse_args())

    # Configure logger
    if (config['verbose']):
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logging.basicConfig(level=logging_level, format="%(message)s")

    # Create configuration structure
    firstpage, lastpage = get_pages(config['pages'])
    conf = Conf(firstpage, lastpage, config['force'], config['use_labels'],
                config['all_images'])

    # Call main function
    download_iiif_files(config['manifest'], config['directory'], conf)
