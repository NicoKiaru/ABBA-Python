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

    # download test sections
    basePath = os.getcwd() + '/images/'
    download_test_images(basePath)

    # import sections into ABBA
    files = [basePath + section for section in demo_sections]
    abba.import_from_files(filepaths=files)
    # all registrations are performed on the selected slices.
    # since we want to register all of them, we select all of them
    abba.select_all_slices()

    # we want to avoid saturation in the display. This does not matter for
    # all registration methods EXCEPT for DeepSlice, which takes in rgb images
    abba.change_display_settings(0, 0, 500)
    abba.change_display_settings(1, 0, 1200)

    # a first deepslice registration round : possible because it's the Allen CCF atlas, cut in coronal mode
    # what's assumed : the sections are already in the correct order
    abba.register_slices_deepslice(channels=[0, 1])

    # second deepslice registration: because the slices are resampled for the registration,
    # we usually get a slightly better positioning along z and cutting angle
    # also: it's fast, and the combination of two affine transforms is
    # an affine transform, so it's not like we are adding extra degrees of freedom
    abba.register_slices_deepslice(channels=[0, 1])

    # a round of elastix registration, affine
    # the channel 0 of the dataset (DAPI) is registered with the Nissl Channel of the atlas (0)
    # and the channel 1 of the dataset (mainly autofluo) is registered with the autofluo channel of the atlas (1)
    # these two channels have equal weights in the registration process
    abba.register_slices_elastix_affine(channels_slice_csv='0,1',
                                        channels_atlas_csv='0,1',
                                        pixel_size_micrometer=40)

    # optional: a round of elastix registration, spline
    # same channels as in the affine registration
    # 5 control points along x = very coarse spline (and thus maybe unnecessary)
    # abba.register_elastix_spline(
    #    nb_control_points=5,
    #    atlas_image_channels=[0, 1],
    #    slice_image_channels=[0, 1],
    #    pixel_size_micrometer=40)

    # a round of elastix registration, affine
    # same channels as in the affine registration
    # 16 control points = reasonable spline, which allows for local corrections, without deforming two much the section
    abba.register_slices_elastix_spline(channels_slice_csv='0,1',
                                        channels_atlas_csv='0,1',
                                        nb_control_points_x=16,
                                        pixel_size_micrometer=20)


    # everything will close 10 hours after the registration is done...
    time.sleep(36000)  # Humm, because ij closes if the python process closes
