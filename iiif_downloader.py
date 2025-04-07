"""Download all images from an IIIF manifest."""

import logging
from re import match
import argparse
import json
import time
import os
from shutil import rmtree
from urllib.request import urlopen, Request
from typing import List, Tuple, Dict, Any


class Conf:
    """A class containing all user configurations."""
    def __init__(self, firstpage: int = 1, lastpage: int = -1,
                 use_labels: bool = False, force: bool = False):
        self.firstpage = firstpage
        self.lastpage = lastpage
        self.use_labels = use_labels
        self.force = force


class Info:
    """A class containing the features of an IIIF file."""
    def __init__(self, label: str = "NA", iiif_id: str = "NA",
                 iiif_format: str = "NA", iiif_w: int = 0, iiif_h: int = 0):
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


def open_url(u: str):
    """Open url."""
    headers = {'User-Agent': "Mozilla/5.0"}
    try:
        response = urlopen(Request(u, headers=headers), timeout=30)
        return response
    except Exception as err:
        logging.error(err)
        return None


def download_file(u: str, filepath: str) -> int:
    """Open a remote file and save it locally."""
    u = u.replace(" ", "%20")
    logging.debug("- Downloading " + u)

    # Read the remote file from url
    res = open_url(u)
    # logging.info(res.getcode())
    if (res is None):
        return -1

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

    # Read label (it is not guaranteed to be a string)
    manifest_label = str(d.get('label'))
    assert manifest_label is not None, "'label' not found."

    # Read id
    manifest_id = d.get('@id')
    assert manifest_id is not None, "'@id' not found."

    # Read sequences
    sequences = d.get('sequences')
    assert sequences is not None, "'sequences' not found."
    # [Assumption #1] 1 sequence in sequences
    sequence = sequences[0]
    # assert sequence.get("@type") == 'sc:Sequence'

    # Read canvases
    canvases = sequence.get("canvases")
    infos = []
    for c in canvases:
        # assert c.get("@type") == 'sc:Canvas'

        # Create empty info node
        i = Info()

        # Read label
        label = c.get("label", "NA")
        i.label = label

        # Read width and height
        iiif_w = c.get('width', 0)
        iiif_h = c.get('height', 0)
        i.w = iiif_w
        i.h = iiif_h

        # Read image
        images = c.get("images")
        if (images is not None):
            # [Assumption #2] 1 image in images
            img = images[0]
            # assert img.get('@type') == "oa:Annotation"
            # assert img.get('motivation') == "sc:painting"

            resource = img.get("resource")

            # if resource has multiple images (choice), take default only
            if (resource.get('@type') == "oa:Choice"):
                resource = resource.get('default')

            # "The image MUST have an @id field [...] Its media
            # type MAY be listed in format"
            iiif_id = resource.get('@id')
            assert iiif_id is not None, "'@id' not found."
            i.id = iiif_id

            iiif_format = resource.get('format', 'NA')
            i.format = iiif_format

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

    # Read label
    manifest_label = d.get('label')
    assert manifest_label is not None, "'label' not found."
    if (isinstance(manifest_label, dict)):
        manifest_label = next(iter(manifest_label.values()))  # First value
    manifest_label = manifest_label[0]

    # Read id
    manifest_id = d.get('id')
    assert manifest_id is not None, "'id' not found."

    # Read canvas
    items: Any = d.get('items')
    infos = []
    for it in items:
        # assert it.get('type') == "Canvas"

        # Create empty info node
        i = Info()

        label = it.get('label', 'NA')
        if (isinstance(label, dict)):
            label = next(iter(label.values()))  # First value
        label = label[0]
        i.label = label

        if (len(it.get('items')) > 0):
            # Read annotation page
            annotation_page = it.get('items')
            assert annotation_page is not None, \
                "'items' (annotation page) not found."
            # [Assumption #1] 1 annotation page in canvas
            annotation_page = annotation_page[0]

            # Read annotation
            # assert annotation_page.get('type') == "AnnotationPage"
            annotation = annotation_page.get('items')
            assert annotation is not None, "'items' (annotation) not found."
            # [Assumption #2] 1 annotation in annotation page
            annotation = annotation[0]
            # assert annotation.get('type') == "Annotation"

            # Read body or body.source
            body = annotation.get('body')

            body_type = body.get('type')
            if (body_type == 'Image'):
                source = body
            elif (body_type == 'SpecificResource'):
                source = body.get('source')
            else:
                raise Exception("Unsupported body type: " + body_type)

            iiif_id = source.get('id')
            i.id = iiif_id

            iiif_format = source.get('format')
            i.format = iiif_format

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
        raise Exception('Unsupported IIIF version (' + str(version) + ')')

    # Print manifest features
    logging.debug('- IIIF version: ' + str(version) + '.0')
    logging.debug('- Manifest ID: ' + manifest_id)
    logging.info('- Title: ' + manifest_label)
    logging.info('- Files: ' + str(len(infos)))

    if (len(infos) > 0):
        # Create subdirectory from manifest label
        subdir = maindir + '/' + sanitize_name(manifest_label)
        if (not os.path.exists(subdir)):
            os.mkdir(subdir)
            logging.debug(
                '- ' + sanitize_name(manifest_label) + ' created in '
                + maindir)

        # Create sub-array (conf.firstpage, conf.lastpage)
        totpages = len(infos)
        if (conf.firstpage != 1 or conf.lastpage != -1):
            infos = infos[conf.firstpage - 1:]
            infos = infos[:conf.lastpage - conf.firstpage + 1]
            logging.info(
                "- Downloading pages " + str(conf.firstpage) + "-"
                + str(conf.lastpage) + " from a total of " + str(totpages))

        # Loop over each id
        some_error = False
        try_with_id = True
        total_filesize = 0
        downloaded_cnt = 0
        start_time = time.time()
        for cnt, info in enumerate(infos):
            # Print counters and label
            percentage = round((cnt + 1) / len(infos) * 100, 1)
            cnt = cnt + conf.firstpage - 1
            logging.info('[n.' + str(cnt + 1) + '/' + str(totpages) + '; '
                         + str(percentage) + '%] Label: ' + info.label)

            # Print file ID
            logging.info('- ID: ' + info.id)
            if (info.id == 'NA'):
                logging.debug('- File not available in the manifest, skip')
                continue

            # Print file extension
            ext = get_extension(info.format)
            # If the format was not found, try to take extension from file name
            if (ext == 'NA' and '.' in info.id):
                ext = '.' + info.id.split('.')[-1]
            logging.info('- Format: ' + info.format + ' => Extension: ' + ext)

            # Print file dimensions
            logging.info('- Width: ' + str(info.w) + ' px')
            logging.info('- Height: ' + str(info.h) + ' px')

            # Download file
            if (conf.use_labels):
                filename = sanitize_name(info.label) + ext
            else:
                filename = 'p' + str(cnt + 1).zfill(3) + ext

            if (os.path.exists(subdir + '/' + filename) and not conf.force):
                logging.debug('- ' + subdir + '/' + filename + " exists, skip")
                continue

            # Priority to image id, but if it doesn't work, we move
            # to URI template and we stop trying with it
            filesize = -1
            if (try_with_id):
                filesize = download_file(info.id, subdir + '/' + filename)
                if (filesize <= 0):
                    logging.debug("- Cannot download " + info.id)
                    try_with_id = False

            if (filesize <= 0):
                img_url = get_img_url(info.id, ext)
                filesize = download_file(img_url, subdir + '/' + filename)

            # Print final message and update counters
            if (filesize <= 0):
                logging.error('\033[91m' + '- Error!' + '\033[0m')
                some_error = True
            else:
                logging.info(
                    '\033[92m' + '- ' + filename + ' ('
                    + str(round(filesize / 1000)) + ' KB) saved in '
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
        raise Exception("Unsupported IIIF version (context: " + context + ')')

    return version


def download_iiif_files(json_file: str, maindir: str,
                        conf: Conf = Conf()) -> None:
    """Download all the files from a manifest or a collection."""
    # Check if json file is local or remote and read it
    if (is_url(json_file)):
        d = json.loads(open_url(json_file).read())
    else:
        with open(json_file) as f:
            d = json.load(f)

    # Check IIIF version
    version = get_iiif_version(d)

    # Check if the input file is a manifest or a collection
    if (version == 2):
        type_key = '@type'
        manifest_string = 'sc:Manifest'
        collection_string = 'sc:Collection'
        manifests_key = 'manifests'
        id_key = '@id'
    else:
        type_key = 'type'
        manifest_string = 'Manifest'
        collection_string = 'Collection'
        manifests_key = 'items'
        id_key = 'id'

    iiif_type = str(d.get(type_key))
    if (iiif_type.lower() == manifest_string.lower()):
        download_iiif_files_from_manifest(version, d, maindir, conf)
    elif (iiif_type.lower() == collection_string.lower()):
        # TODO: one directory for same collection?
        manifests = d.get(manifests_key)
        for m in manifests:
            manifest_id = m.get(id_key)
            d = json.loads(open_url(manifest_id).read())
            download_iiif_files_from_manifest(version, d, maindir, conf)
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
    # Parse arguments
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

    config = vars(parser.parse_args())

    # Create configuration structure
    firstpage, lastpage = get_pages(config['pages'])
    conf = Conf(firstpage, lastpage, config['use_labels'], config['force'])

    # Configure logger
    if (config['verbose']):
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logging.basicConfig(level=logging_level, format="%(message)s")

    # Call main function
    download_iiif_files(config['manifest'], config['directory'], conf)
