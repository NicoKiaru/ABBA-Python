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
        utils.check_internet_connection()
        url = 'https://zenodo.org/record/6592478/files/' + section_name + '?download=1'
        utils.retrieve_over_http(url, outputPath)
    else:
        pass

demo_sections = [
    'S00.tif',
#    'S05.tif',
    'S10.tif',
#    'S15.tif',
    'S20.tif',
#    'S25.tif',
    'S30.tif',
#    'S35.tif',
    'S40.tif',
#    'S45.tif',
    'S50.tif',
#    'S55.tif',
    'S60.tif',
#    'S65.tif',
    'S70.tif',
#    'S75.tif',
    'S80.tif']

def download_test_images(basePath):
    [downloadIfNecessary(basePath, section) for section in demo_sections]


if __name__ == '__main__':
    # abba = Abba("allen_mouse_25um") # any BrainGlobe atlas
    abba = Abba('Adult Mouse Brain - Allen Brain Atlas V3')
    abba.show_bdv_ui()  # creates and show a bdv view

    # download test sections
    basePath = os.getcwd() + '/images/'
    download_test_images(basePath)

    # import sections into ABBA
    files = [basePath + section for section in demo_sections]
    abba.import_from_files(filepaths=files).get()  # .get() to wait for the request to finish
    print('Hmpf')
    # all registrations are performed on the selected slices.
    # since we want to register all of them, we select all of them
    abba.select_all_slices()

    # we want to avoid saturation in the display. This does not matter for
    # all registration methods EXCEPT DeepSlice, which takes rgb images
    print("channel 1 change")
    abba.change_display_settings(0, 0, 500)
    print("channel 2 change")
    abba.change_display_settings(1, 0, 1200)
    print("channels changed")

    # first deepslice registration round : possible because it's the Allen CCF atlas, cut in coronal mode
    # what's assumed : the sections are already in the correct order
    # only the dapi channel is used for the registration
    abba.register_slices_deepslice(channels=[0, 1])

    # second deepslice registration: it's fast, and because the new position is resampled,
    # we usually get slightly better positioning along z
    abba.register_slices_deepslice(channels=[0, 1])

    # a round of elastix registration, affine
    # the channel 0 of the dataset (DAPI) is registered with the Nissl Channel of the atlas (0)
    # and the channel 1 of the dataset (mainly autofluo) is registered with the autofluo channel of the atlas (1)
    # these two channels have equal weights in the registration process
    abba.register_slices_elastix_affine(channels_slice_csv='0,1',
                                        channels_atlas_csv='0,1',
                                        pixel_size_micrometer=40)

    # a round of elastix registration, affine
    # same channels as in the affine registration
    # 5 control points along x = very coarse spline (and thus maybe unnecessary)
    #abba.register_elastix_spline(
    #    nb_control_points=5,
    #    atlas_image_channels=[0, 1],
    #    slice_image_channels=[0, 1],
    #    pixel_size_micrometer=40).get()

    # a round of elastix registration, affine
    # same channels as in the affine registration
    # 16 control points = reasonable spline, which allows for local corrections, without deforming two much the section
    abba.register_slices_elastix_spline(channels_slice_csv='0,1',
                                        channels_atlas_csv='0,1',
                                        nb_control_points_x=16,
                                        pixel_size_micrometer=20)



    # eveything will close 10 hours after the registration is done...
    time.sleep(36000)  # Humm, because ij 