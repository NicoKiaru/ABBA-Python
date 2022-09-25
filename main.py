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


def download_test_images(basePath):
    utils.check_internet_connection()
    downloadIfNecessary(basePath, 'S00.tif')
    downloadIfNecessary(basePath, 'S10.tif')
    downloadIfNecessary(basePath, 'S20.tif')
    downloadIfNecessary(basePath, 'S30.tif')
    downloadIfNecessary(basePath, 'S40.tif')
    downloadIfNecessary(basePath, 'S50.tif')
    downloadIfNecessary(basePath, 'S60.tif')
    downloadIfNecessary(basePath, 'S70.tif')
    downloadIfNecessary(basePath, 'S80.tif')


if __name__ == '__main__':
    atlas = BrainGlobeAtlas("allen_mouse_25um")
    abba = Abba(atlas)
    abba.ij.ui().showUI()  # Comment to remove Fiji's main bar, but then you will loose the nice flatlaf layout
    abba.show_bdv_ui()  # creates and show a bdv view

    basePath = os.getcwd() + '/images/'
    download_test_images(basePath)

    abba.import_from_files(
        filepaths=[basePath + 'S00.tif',
                   basePath + 'S10.tif',
                   basePath + 'S20.tif',
                   basePath + 'S30.tif',
                   basePath + 'S40.tif',
                   basePath + 'S50.tif',
                   basePath + 'S60.tif',
                   basePath + 'S70.tif',
                   basePath + 'S80.tif']).get()  # .get() to wait for the request to finish

    time.sleep(25000)  # Humm, because ij closes immediately if the python process is finished (dirty workaround)
