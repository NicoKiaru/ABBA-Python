# Main class for demoing the abba package

import time
from bg_atlasapi.bg_atlas import BrainGlobeAtlas

import os
from bg_atlasapi import utils
from pathlib import Path
from abba import Abba

def downloadIfNecessary(basePath, section_name):
    outputPath = Path(basePath + section_name)
    if not outputPath.exists():
        url = 'https://zenodo.org/record/6592478/files/' + section_name + '?download=1'
        utils.retrieve_over_http(url, outputPath)
    else:
        pass

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

def download_test_images(basePath):
    utils.check_internet_connection()
    [downloadIfNecessary(basePath, section) for section in demo_sections]


if __name__ == '__main__':
    # atlas = BrainGlobeAtlas("allen_mouse_25um")
    # abba = Abba("allen_mouse_25um")
    abba = Abba() # no parameter = Allen Mouse Brain CCFv3
    abba.show_bdv_ui()  # creates and show a bdv view

    basePath = os.getcwd() + '/images/'
    download_test_images(basePath)

    files = [basePath + section for section in demo_sections]

    abba.import_from_files(
        filepaths=files).get()  # .get() to wait for the request to finish

    abba.mp.selectSlice(abba.mp.getSlices())  # select all

    abba.register_deepslice(channels=[0]).get()
    abba.register_deepslice(channels=[0]).get()

    abba.register_elastix_affine(atlas_image_channels=[0, 1],
                                 slice_image_channels=[0, 1]).get()

    abba.register_elastix_spline(
        nb_control_points=5,
        atlas_image_channels=[0, 1],
        slice_image_channels=[0, 1],
        pixel_size_micrometer=40).get()

    abba.register_elastix_spline(
        nb_control_points=12,
        atlas_image_channels=[0, 1],
        slice_image_channels=[0, 1],
        pixel_size_micrometer=20).get()

    time.sleep(25000)  # Humm, because ij closes immediately if the python process is finished (dirty workaround)