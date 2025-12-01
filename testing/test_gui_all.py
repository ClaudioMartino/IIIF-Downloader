from test_common import Test
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader  # import ../iiif_downloader.py
import iiif_downloader_gui  # import ../iiif_downloader_gui.py
import logging
import argparse
from tkinter import Tk


# One global window for all GUI tests
window = Tk()


class TestGui(Test):
    def __init__(self, ref):
        # Test constructor for ref
        super().__init__(ref)

        # Create GUI
        self.gui = iiif_downloader_gui.GUI(window)

        # Set dummy values in GUI to avoid unrelated exceptions
        self.gui.manifest_url.set("http://dummy-manifest.fake")
        self.gui.path.set("dummy_destination_folder")

        # Create downloader in GUI
        self.gui.downloader = iiif_downloader.IIIF_Downloader()


class TestGUI_manifest(TestGui):
    def run(self, manifest_radio, manifest_url, manifest_file):
        # Set manifest in GUI
        self.gui.manifest_radio.set(manifest_radio)
        self.gui.manifest_url.set(manifest_url)
        self.gui.manifest_file.set(manifest_file)

        # Read GUI values
        self.gui.read_and_check_values()

        # Read downloader value
        self.result = self.gui.downloader.json_file


class TestGUI_maindir(TestGui):
    def run(self, maindir):
        # Set maindir in GUI
        self.gui.path.set(maindir)

        # Read GUI values
        self.gui.read_and_check_values()

        # Read downloader value
        self.result = self.gui.downloader.maindir


class TestGUI_pages(TestGui):
    def run(self, pages_radio, pages_range):
        # Set pages in GUI
        self.gui.pages_radio.set(pages_radio)
        self.gui.pages_range.set(pages_range)

        # Read GUI values
        self.gui.read_and_check_values()

        # Read downloader value
        self.result = [self.gui.downloader.firstpage, self.gui.downloader.lastpage]


class TestGUI_force(TestGui):
    def run(self, force_flag):
        # Set force flag in GUI
        self.gui.force.set(int(force_flag))

        # Read GUI values
        self.gui.read_and_check_values()

        # Read downloader value
        self.result = self.gui.downloader.force


class TestGUI_uselabels(TestGui):
    def run(self, uselabels_flag):
        # Set use labels flag in GUI
        self.gui.uselabels.set(int(uselabels_flag))

        # Read GUI values
        self.gui.read_and_check_values()

        # Read downloader value
        self.result = self.gui.downloader.use_labels


class TestGUI_allimages(TestGui):
    def run(self, allimages_flag):
        # Set all images flag in GUI
        self.gui.allimages.set(int(allimages_flag))

        # Read GUI values
        self.gui.read_and_check_values()

        # Read downloader value
        self.result = self.gui.downloader.all_images


class TestGUI_referer(TestGui):
    def run(self, referer_radio, referer):
        # set referer value in GUI
        self.gui.referer_radio.set(referer_radio)
        self.gui.referer.set(referer)

        # Read GUI values
        self.gui.read_and_check_values()

        # Read downloader value
        self.result = self.gui.downloader.referer


class TestGUI_threads(TestGui):
    def run(self, num_threads):
        # Set threads in GUI
        self.gui.threads.set(num_threads)

        # Read GUI values
        self.gui.read_and_check_values()

        # Read downloader value
        self.result = self.gui.downloader.num_threads


class TestGUI_width(TestGui):
    def run(self, width_radio, custom_width):
        # Set width in GUI
        self.gui.width_radio.set(width_radio)
        self.gui.custom_width.set(custom_width)

        # Read GUI values
        self.gui.read_and_check_values()

        # Read downloader value
        self.result = self.gui.downloader.width


# MAIN: Check if the values set in the GUI are correctly passed to downloader

# Set logger level
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# TODO exception catch
logging.info("Test GUI manifest")
manifest_radios = ["url", "file"]
manifest_urls = ["https://www.manifest.test", "not-used"]
manifest_files = ["not-used", "path/to/manifest/file"]
refs = ["https://www.manifest.test", "path/to/manifest/file"]
for manifest_radio, manifest_url, manifest_file, ref in zip(manifest_radios, manifest_urls, manifest_files, refs):
    test = TestGUI_manifest(ref)
    test.run(manifest_radio, manifest_url, manifest_file)
    test.check_ref()

logging.info("Test GUI main directory")
gui_maindir = "main/directory/"
ref = gui_maindir
test = TestGUI_maindir(ref)
test.run(gui_maindir)
test.check_ref()

logging.info("Test GUI pages")
gui_pages_radios = ["range", "range", "all"]
gui_pages_ranges = ["1-99", "1-1", "not-used"]
refs = [[1, 99], [1, 1], [1, -1]]
for pages_radio, pages_range, ref in zip(gui_pages_radios, gui_pages_ranges, refs):
    test = TestGUI_pages(ref)
    test.run(pages_radio, pages_range)
    test.check_ref()

logging.info("Test GUI check buttons")
check_buttons = [True, False]
refs = check_buttons
for check_button, ref in zip(check_buttons, refs):
    test = TestGUI_force(ref)
    test.run(check_button)
    test.check_ref()

    test = TestGUI_uselabels(ref)
    test.run(check_button)
    test.check_ref()

    test = TestGUI_allimages(ref)
    test.run(check_button)
    test.check_ref()

logging.info("Test GUI referer")
referer_radios = ["default", "custom"]
referers = [None, "https://custom.referer"]
refs = referers
for referer_radio, referer, ref in zip(referer_radios, referers, refs):
    test = TestGUI_referer(ref)
    test.run(referer_radio, referer)
    test.check_ref()

logging.info("Test GUI threads")
gui_threads = "16"
ref = int(gui_threads)
test = TestGUI_threads(ref)
test.run(gui_threads)
test.check_ref()

logging.info("Test GUI width")
width_radios = ["highest", "host", "custom"]
custom_widths = ["not-used", "not-used", 1024]
refs = [0, None, 1024]  # -w unused: 0; -w without arg: None
for width_radio, custom_width, ref in zip(width_radios, custom_widths, refs):
    test = TestGUI_width(ref)
    test.run(width_radio, custom_width)
    test.check_ref()
