import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader  # import ../iiif_downloader.py
import iiif_downloader_gui  # import ../iiif_downloader_gui.py
import logging
import argparse
from tkinter import Tk


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

class TestGUI_manifest(Test):
    def run(self, window, manifest_radio, manifest_url, manifest_file):
        # Create default GUI
        gui = iiif_downloader_gui.GUI(window)

        # Set manifest in GUI
        gui.manifest_radio.set(manifest_radio)
        gui.manifest_url.set(manifest_url)
        gui.manifest_file.set(manifest_file)

        # Set dummy value in GUI to avoid unrelated exception
        gui.path.set("dummy_destination_folder")

        # Create downloader and read GUI value
        gui.downloader = iiif_downloader.IIIF_Downloader()
        gui.read_and_check_values()

        # Read downloader value
        self.result = gui.downloader.json_file


class TestGUI_maindir(Test):
    def run(self, window, maindir):
        # Create default GUI
        gui = iiif_downloader_gui.GUI(window)

        # Set maindir in GUI
        gui.path.set(maindir)

        # Set dummy values in GUI to avoid unrelated exception
        gui.manifest_url.set("http://dummy-manifest.fake")

        # Create downloader and read GUI value
        gui.downloader = iiif_downloader.IIIF_Downloader()
        gui.read_and_check_values()

        # Read downloader value
        self.result = gui.downloader.maindir


class TestGUI_pages(Test):
    def run(self, window, pages_radio, pages_range):
        # Create default GUI
        gui = iiif_downloader_gui.GUI(window)

        # Set pages in GUI
        gui.pages_radio.set(pages_radio)
        gui.pages_range.set(pages_range)

        # Set dummy values in GUI to avoid unrelated exception
        gui.manifest_url.set("http://dummy-manifest.fake")
        gui.path.set("dummy_destination_folder")

        # Create downloader and read GUI value
        gui.downloader = iiif_downloader.IIIF_Downloader()
        gui.read_and_check_values()

        # Read downloader value
        self.result = [gui.downloader.firstpage, gui.downloader.lastpage]


class TestGUI_force(Test):
    def run(self, window, force_flag):
        # Create default GUI
        gui = iiif_downloader_gui.GUI(window)

        # Set force flag in GUI
        gui.force.set(int(force_flag))

        # Set dummy values in GUI to avoid unrelated exception
        gui.manifest_url.set("http://dummy-manifest.fake")
        gui.path.set("dummy_destination_folder")

        # Create downloader and read GUI value
        gui.downloader = iiif_downloader.IIIF_Downloader()
        gui.read_and_check_values()

        # Read downloader value
        self.result = gui.downloader.force


class TestGUI_uselabels(Test):
    def run(self, window, uselabels_flag):
        # Create default GUI
        gui = iiif_downloader_gui.GUI(window)

        # Set use labels flag in GUI
        gui.uselabels.set(int(uselabels_flag))

        # Set dummy values in GUI to avoid unrelated exception
        gui.manifest_url.set("http://dummy-manifest.fake")
        gui.path.set("dummy_destination_folder")

        # Create downloader and read GUI value
        gui.downloader = iiif_downloader.IIIF_Downloader()
        gui.read_and_check_values()

        # Read downloader value
        self.result = gui.downloader.use_labels


class TestGUI_allimages(Test):
    def run(self, window, allimages_flag):
        # Create default GUI
        gui = iiif_downloader_gui.GUI(window)

        # Set all images flag in GUI
        gui.allimages.set(int(allimages_flag))

        # Set dummy values in GUI to avoid unrelated exception
        gui.manifest_url.set("http://dummy-manifest.fake")
        gui.path.set("dummy_destination_folder")

        # Create downloader and read GUI value
        gui.downloader = iiif_downloader.IIIF_Downloader()
        gui.read_and_check_values()

        # Read downloader value
        self.result = gui.downloader.all_images


class TestGUI_referer(Test):
    def run(self, window, referer_radio, referer):
        # Create default GUI
        gui = iiif_downloader_gui.GUI(window)

        # set referer value in GUI
        gui.referer_radio.set(referer_radio)
        gui.referer.set(referer)

        # Set dummy values in GUI to avoid unrelated exception
        gui.manifest_url.set("http://dummy-manifest.fake")
        gui.path.set("dummy_destination_folder")

        # Create downloader and read GUI value
        gui.downloader = iiif_downloader.IIIF_Downloader()
        gui.read_and_check_values()

        # Read downloader value
        self.result = gui.downloader.referer


class TestGUI_threads(Test):
    def run(self, window, num_threads):
        # Create default GUI
        gui = iiif_downloader_gui.GUI(window)

        # Set threads in GUI
        gui.threads.set(num_threads)

        # Set dummy values in GUI to avoid unrelated exception
        gui.manifest_url.set("http://dummy-manifest.fake")
        gui.path.set("dummy_destination_folder")

        # Create downloader and read GUI value
        gui.downloader = iiif_downloader.IIIF_Downloader()
        gui.read_and_check_values()

        # Read downloader value
        self.result = gui.downloader.num_threads


class TestGUI_width(Test):
    def run(self, window, width_radio, custom_width):
        # Create default GUI
        gui = iiif_downloader_gui.GUI(window)

        # Set width in GUI
        gui.width_radio.set(width_radio)
        gui.custom_width.set(custom_width)

        # Set dummy values in GUI to avoid unrelated exception
        gui.manifest_url.set("http://dummy-manifest.fake")
        gui.path.set("dummy_destination_folder")

        # Create downloader and read GUI value
        gui.downloader = iiif_downloader.IIIF_Downloader()
        gui.read_and_check_values()

        # Read downloader value
        self.result = gui.downloader.width


# MAIN: Check if the values set in the GUI are correctly passed to downloader

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

window = Tk()  # One window for all GUI tests

# TODO exception catch
logging.info("Test GUI manifest")
manifest_radios = ["url", "file"]
manifest_urls = ["https://www.manifest.test", "not-used"]
manifest_files = ["not-used", "path/to/manifest/file"]
refs = ["https://www.manifest.test", "path/to/manifest/file"]
for manifest_radio, manifest_url, manifest_file, ref in zip(manifest_radios, manifest_urls, manifest_files, refs):
    test = TestGUI_manifest(ref)
    test.run(window, manifest_radio, manifest_url, manifest_file)
    test.check_ref()

logging.info("Test GUI main directory")
gui_maindir = "main/directory/"
ref = gui_maindir
test = TestGUI_maindir(ref)
test.run(window, gui_maindir)
test.check_ref()

logging.info("Test GUI pages")
gui_pages_radios = ["range", "range", "all"]
gui_pages_ranges = ["1-99", "1-1", "not-used"]
refs = [[1, 99], [1, 1], [1, -1]]
for pages_radio, pages_range, ref in zip(gui_pages_radios, gui_pages_ranges, refs):
    test = TestGUI_pages(ref)
    test.run(window, pages_radio, pages_range)
    test.check_ref()

logging.info("Test GUI check buttons")
check_buttons = [True, False]
refs = check_buttons
for check_button, ref in zip(check_buttons, refs):
    test = TestGUI_force(ref)
    test.run(window, check_button)
    test.check_ref()

    test = TestGUI_uselabels(ref)
    test.run(window, check_button)
    test.check_ref()

    test = TestGUI_allimages(ref)
    test.run(window, check_button)
    test.check_ref()

logging.info("Test GUI referer")
referer_radios = ["default", "custom"]
referers = [None, "https://custom.referer"]
refs = referers
for referer_radio, referer, ref in zip(referer_radios, referers, refs):
    test = TestGUI_referer(ref)
    test.run(window, referer_radio, referer)
    test.check_ref()

logging.info("Test GUI threads")
gui_threads = "16"
ref = int(gui_threads)
test = TestGUI_threads(ref)
test.run(window, gui_threads)
test.check_ref()

logging.info("Test GUI width")
width_radios = ["highest", "host", "custom"]
custom_widths = ["not-used", "not-used", 1024]
refs = [0, None, 1024]  # -w unused: 0; -w without arg: None
for width_radio, custom_width, ref in zip(width_radios, custom_widths, refs):
    test = TestGUI_width(ref)
    test.run(window, width_radio, custom_width)
    test.check_ref()
