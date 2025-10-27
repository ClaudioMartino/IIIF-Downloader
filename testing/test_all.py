import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader  # import ../iiif_downloader.py
import json
import logging
import argparse
from test_data import ver_dict


class Test:
    def __init__(self, ref):
        self.ref = ref
        self.result = None

    def check_ref(self):
        if (self.result != self.ref):
            raise Exception(
                "Error! Result: " + str(self.result) + " (" +
                str(type(self.result)) + "). Ref.: " + str(self.ref) + " (" +
                str(type(self.ref)) + ")")


# Test child classes


class TestSanitizeLabel(Test):
    def run(self, label):
        self.result = iiif_downloader.sanitize_label(label, "")


class TestGetExtension(Test):
    def run(self, mime_type, file_id):
        self.result = iiif_downloader.get_extension(mime_type, file_id, 0)


class TestMatchURIPattern(Test):
    def run(self, uri):
        status = iiif_downloader.match_uri_pattern(uri)
        self.result = {
            'base':     status.group('base'),
            'region':   status.group('region'),
            'size':     status.group('size'),
            'rotation': status.group('rotation'),
            'quality':  status.group('quality'),
            'format':   status.group('format')
        }


class TestSanitizeName(Test):
    def run(self, title):
        self.result = iiif_downloader.sanitize_name(title)


class TestIsUrl(Test):
    def run(self, url):
        self.result = iiif_downloader.is_url(url)


class TestReadManifest_GetVersion(Test):
    def run(self, file_name):
        downloader = iiif_downloader.IIIF_Downloader()

        d = iiif_downloader.open_json_file(file_name, "")
        downloader.get_iiif_version(d)
        self.result = downloader.version


class TestReadManifest_TotInfo(Test):
    def run(self, file_name, version):
        downloader = iiif_downloader.IIIF_Downloader()
        downloader.json_file = file_name

        if (version == '2'):
            reader = downloader.read_iiif_manifest2
        else:
            reader = downloader.read_iiif_manifest3

        with open(downloader.json_file) as f:
            infos = reader(json.load(f))
            self.result = len(infos)


class TestReadManifest_TotNA(Test):
    def run(self, file_name, version):
        downloader = iiif_downloader.IIIF_Downloader()
        downloader.json_file = file_name

        if (version == '2'):
            reader = downloader.read_iiif_manifest2
        else:
            reader = downloader.read_iiif_manifest3

        with open(downloader.json_file) as f:
            infos = reader(json.load(f))
            na_cnt = 0
            for info in infos:
                if (len(info.id) == 0):
                    na_cnt += 1
            self.result = na_cnt


# MAIN


# Set parser and verbosity
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "-v", "--verbose", default=logging.INFO, action="store_const",
    dest="logging_level", const=logging.DEBUG,
    help="Print a verbose output")
parser.add_argument(
    "-q", "--quiet", default=logging.INFO, action="store_const",
    dest="logging_level", const=logging.ERROR,
    help="Activate quiet mode and print only error messages")
parser_args = vars(parser.parse_args())
logging.basicConfig(level=parser_args["logging_level"], format="%(message)s")


# TEST SANITIZE LABEL
logging.info("Test sanitize label")

labels = [
    "string_to_test",
    ["string_to_test"],
    ["string_to_test", "string_to_test_2"],
    {"@value": "string_to_test"},
    {"key": "val"},
    100,
]

refs = [
    "string_to_test",
    "string_to_test",
    "string_to_test",
    "string_to_test",
    "None",
    "100",
]

for label, ref in zip(labels, refs):
    test = TestSanitizeLabel(ref)
    test.run(label)
    test.check_ref()

# TEST GET EXTENSION
logging.info("Test get extension")

mime_types = [
    "image/jpeg",
    "image/jpg",
    "image/tiff",
    "image/png",
    "image/gif",
    "image/jp2",
    "application/pdf",
    "image/webp",
    "something/else",
]

refs = [
    ".jpg",
    ".jpg",
    ".tif",
    ".png",
    ".gif",
    ".jp2",
    ".pdf",
    ".webp",
    "NA",
]

for mime_type, ref in zip(mime_types, refs):
    test = TestGetExtension(ref)
    test.run(mime_type, "file_id")
    test.check_ref()

# Checking priority to extension taken from default.ext file ID
for mime_type in mime_types:
    for ref in refs[:-1]:  # remove NA from refs
        test = TestGetExtension(ref)
        test.run(mime_type, "path/to/file/default" + ref)
        test.check_ref()


# TEST MATCH URI PATTERN
logging.info("Test match URI pattern")

uri_base = "https://content.staatsbibliothek-berlin.de/dc/785884734-0001"
region_list = ["full", "square", "125,15,120,140", "pct:41.6,7.5,40,70"]
size_list = ["full", "max", "^max", "150,", "^360,", ",150", ",^240", "pct:50",
             "pct:120", "225,100", "^360,360", "!225,100", "^!360,360"]
rotation_list = ["0", "22.5", "!0"]
quality_list = ["color", "gray", "bitonal", "default"]
format_list = ["jpg", "tif", "png", "gif", "jp2", "pdf", "webp"]

for r in region_list:
    for s in size_list:
        for rot in rotation_list:
            for q in quality_list:
                for f in format_list:
                    uri = uri_base + '/' + r + '/' + s + '/' + rot + '/' + q + '.' + f
                    ref = {
                        'base': uri_base,
                        'region': r,
                        'size': s,
                        'rotation': rot,
                        'quality': q,
                        'format': f
                    }
                    test = TestMatchURIPattern(ref)
                    test.run(uri)
                    test.check_ref()


# TEST SANITIZE NAME
logging.info("Test sanitize name")

names = [
    "name\\with\\backslashes",
    "name/with/slashes",
    "name:with:colon",
    "name*with*asterisk",
    "name?with?question?marks",
    "name\"with\"quotation\"marks",
    "name<with<less-than<sign",
    "name>with>greater-than>sign",
    "verylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongname",
    "verylongname/with/slashes:and:colonverylongname/with/slashes:and:colonverylongname/with/slashes:and:colonverylongname/with/slashes:and:colon",
]

refs = [
    "name with backslashes",
    "name with slashes",
    "namewithcolon",
    "name with asterisk",
    "namewithquestionmarks",
    "namewithquotationmarks",
    "namewithless-thansign",
    "namewithgreater-thansign",
    "verylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnamevery",
    "verylongname with slashesandcolonverylongname with slashesandcolonverylongname with slashesandcolonv"
]

for name, ref in zip(names, refs):
    test = TestSanitizeName(ref)
    test.run(name)
    test.check_ref()


# TEST IS URL
logging.info("Test is url")

urls = [
    "https://www.wikipedia.org",
    "http://www.wikipedia.org",
    "not_an_url",
]

refs = [
    True,
    True,
    False
]

for url, ref in zip(urls, refs):
    test = TestIsUrl(ref)
    test.run(url)
    test.check_ref()


# TEST READING MANIFESTS
logging.info("Test manifests")

for version in ["2", "3"]:
    for i in range(len(ver_dict[version]['ids'])):
        file_name = 'manifests' + version + '/manifest' + str(i).zfill(2) + '.json'

        # TEST GET VERSION
        ref = int(version)
        test = TestReadManifest_GetVersion(ref)
        test.run(file_name)
        test.check_ref()

        # TEST TOT INFO
        ref = ver_dict[version]['ids'][i]['tot']
        test = TestReadManifest_TotInfo(ref)
        test.run(file_name, version)
        test.check_ref()

        # TEST TOT N/A
        ref = ver_dict[version]['ids'][i]['na']
        test = TestReadManifest_TotNA(ref)
        test.run(file_name, version)
        test.check_ref()
