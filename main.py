# Main class for testing the abba package

import imagej.doctor
import time
from bg_atlasapi.bg_atlas import BrainGlobeAtlas

import os
from bg_atlasapi import utils
from pathlib import Path
from abba import Abba


def downloadIfNecessary(basePath, section_name):
    outputPath = Path(basePath + section_name)
    if not outputPath.exists():
        print('file DO NOT exists')
        #url = 'https://zenodo.org/record/4715656/files/' + section_name + '?download=1'
        #utils.retrieve_over_http(url, outputPath)
    else:
        print('file already exists')

if __name__ == '__main__':
    # imagej.doctor.debug_to_stderr()
    # creates image instance with default dependencies

    # ij.ui().showUI() # uncomment to see Fiji's main bar

    # the import should come after the imagej instance is created,
    # otherwise the Java classes are not discovered


    atlas = BrainGlobeAtlas("allen_mouse_25um")
    abba = Abba(atlas)
    abba.show_bdv_ui()

    cwd = os.getcwd()  # gets current path

    utils.check_internet_connection()
    base_zenodo_url = 'https://zenodo.org/record/4715656/'
    basePath = cwd + '/images/'
    downloadIfNecessary(basePath, 'S30.ome.tiff')  # https://zenodo.org/record/4715656/files/S30.ome.tiff?download=1
    #downloadIfNecessary(basePath, 'S40.ome.tiff')  # https://zenodo.org/record/4715656/files/S40.ome.tiff?download=1
    #downloadIfNecessary(basePath, 'S50.ome.tiff')  # https://zenodo.org/record/4715656/files/S50.ome.tiff?download=1

    basePath = cwd + '/images/'

    time.sleep(25000)


