# core dependencies
import os
import time
from pathlib import Path

# brainglobe dependencies
from bg_atlasapi import show_atlases
from bg_atlasapi import utils

# abba dependency
from abba import Abba

# Demo dataset for automated slices registration
zenodo_demo_slices_url = 'https://zenodo.org/record/6592478/files/'

# Only one section every five section is used for this demo
demo_sections = [
    'S00.tif',
    'S05.tif',
    'S10.tif',
    'S15.tif',
    'S20.tif',
    'S25.tif',
    'S30.tif',
    'S35.tif',
    'S40.tif',
    'S45.tif',
    'S50.tif',
    'S55.tif',
    'S60.tif',
    'S65.tif',
    'S70.tif',
    'S75.tif',
    'S80.tif']


def download_if_necessary(base_path, section_name):
    output_path = Path(base_path + section_name)
    if not output_path.exists():
        utils.check_internet_connection()
        url = zenodo_demo_slices_url + section_name + '?download=1'
        utils.retrieve_over_http(url, output_path)


def download_test_images(base_path):
    [download_if_necessary(base_path, section) for section in demo_sections]


if __name__ == '__main__':
    # -- FOR DEBUGGING
    # import imagej.doctor
    # imagej.doctor.checkup()
    # imagej.doctor.debug_to_stderr()

    # -- Atlas
    # Any brainglobe atlas can be used
    # show_atlases()
    # abba = Abba("azba_zfish_4um", slicing_mode='sagittal', headless=True)  # or any other brainglobe atlas

    # -- HEADLESS
    # abba = Abba('Adult Mouse Brain - Allen Brain Atlas V3', headless=True)  # or any other brainglobe atlas
    # --

    # -- NOT HEADLESS
    abba = Abba('Adult Mouse Brain - Allen Brain Atlas V3')
    abba.show_bdv_ui()  # creates and show a bdv view
    # --

    # everything will close 10 hours after the registration is done...
    time.sleep(36000)  # Humm, because ij closes if the python process closes
