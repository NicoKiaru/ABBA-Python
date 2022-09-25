from bg_atlasapi import BrainGlobeAtlas
from scyjava import jimport
from jpype.types import JString, JArray
import os, shutil
import imagej


def getJavaDependencies():
    """
    Returns the jar files that need to be included into the classpath
    of an imagej object in order to have a functional ABBA app
    these jars should be available in https://maven.scijava.org/
    :return:
    """
    imagej_core_dep = 'net.imagej:imagej:2.9.0'
    imagej_legacy_dep = 'net.imagej:imagej-legacy:0.39.2'
    abba_dep = 'ch.epfl.biop:ImageToAtlasRegister:0.3.3'
    return [imagej_core_dep, imagej_legacy_dep, abba_dep]


class Abba:
    """Abba object which can be used to register sections to a BrainGloabe atlas object
    Parameters
    ----------
    atlas :
        Name of the atlas to be used, should be available in BrainGlobe
    ij :
        ImageJ instance, should be reused if you need to open several ABBA instances
    """

    opened_atlases: dict = {}

    def __init__(
            self,
            atlas_name: str = 'Adult Mouse Brain - Allen Brain Atlas V3',
            ij=None,
            slicing_mode='coronal'  # or sagittal or horizontal
    ):
        if ij is None:
            ij = imagej.init(getJavaDependencies(), mode='interactive')
            self.ij = ij
            ij.ui().showUI() # required I fear

        if atlas_name not in Abba.opened_atlases:
            if atlas_name == 'Adult Mouse Brain - Allen Brain Atlas V3':
                AllenBrainAdultMouseAtlasCCF2017Command = jimport(
                    'ch.epfl.biop.atlas.mouse.allen.ccfv3.command.AllenBrainAdultMouseAtlasCCF2017Command')
                atlas = ij.command().run(AllenBrainAdultMouseAtlasCCF2017Command, True).get().getOutput("ba")
                Abba.opened_atlases[atlas_name] = atlas
            elif atlas_name == 'Rat - Waxholm Sprague Dawley V4':
                WaxholmSpragueDawleyRatV4Command = jimport(
                    'ch.epfl.biop.atlas.rat.waxholm.spraguedawley.v4.command.WaxholmSpragueDawleyRatV4Command')
                atlas = ij.command().run(WaxholmSpragueDawleyRatV4Command, True).get().getOutput("ba")
                Abba.opened_atlases[atlas_name] = atlas
            else:
                bg_atlas = BrainGlobeAtlas("allen_mouse_25um")
                from abba.abba_private import \
                    AbbaAtlas  # delayed import because the jvm should be correctly initialized
                atlas = AbbaAtlas(bg_atlas, ij)
                atlas.initialize(None, None)
                Abba.opened_atlases[atlas_name] = atlas

        self.atlas = Abba.opened_atlases[atlas_name]

        # Initialising ImageJ, if not already initialised
        # Makes the atlas object
        # if atlas is not None:
        #    self.atlas = atlas
        #    from abba.abba_private import AbbaAtlas
        #    self.convertedAtlas = AbbaAtlas(self.atlas, ij)
        #    self.convertedAtlas.initialize(None, None)
        #    # Puts it in the scijava ObjectService for automatic discovery if necessary
        #    ij.object().addObject(self.convertedAtlas)

        # Starts ABBA

        self.slicing_mode = slicing_mode
        self.atlas_name = atlas_name

        # .. but before : logger, please shut up
        DebugTools = jimport('loci.common.DebugTools')
        DebugTools.enableLogging('DEBUG')

        # Ok, let's create abba's model: mp = multipositioner

        ABBAStartCommand = jimport('ch.epfl.biop.atlas.aligner.command.ABBAStartCommand')  # Command import

        self.mp = ij.command().run(ABBAStartCommand, True,
                                   'slicing_mode', self.slicing_mode,
                                   'ba', self.atlas
                                   ).get().getOutput('mp')

    def ij(self):
        """
        Provides the ImageJ instance that can be reused to create another Abba instance
        :return:
            the ImageJ instance used by this Abba instance
        """
        return self.ij

    def show_bdv_ui(self):
        """
        Creates and show a BigDataViewer view over this Abba instance
        """
        if not hasattr(self, 'bdv_view'):
            # no bdv view properties : creates a new one
            SourceAndConverterServices = jimport('sc.fiji.bdvpg.services.SourceAndConverterServices')
            BdvMultislicePositionerView = jimport('ch.epfl.biop.atlas.aligner.gui.bdv.BdvMultislicePositionerView')
            bdvh = SourceAndConverterServices.getBdvDisplayService().getNewBdv()
            self.bdv_view = BdvMultislicePositionerView(self.mp, bdvh)
        else:
            # TODO: make sure it is visible
            pass

    def import_from_files(self, z_location=0, z_increment=0.02, split_rgb=False, filepaths=[]):
        """

        :param z_location:
            initial location in mm along the atlas cutting axis
        :param z_increment:
            step in mm between each imported image
        :param split_rgb:
            whether rgb channels should be split in 3 independent RGB channels (necessary for 16 bits per component RGB images)
        :param filepaths:
            file paths of the image to import. Each file should be readable by bio-formats
        :return:
            a Future object: if you call .get(), the request will wait to be finished. If not, the import
            files command is executed asynchronously
        """
        # Let's import the files using Bio-Formats.
        # The list of all commands is accessible here:
        # https://github.com/BIOP/ijp-imagetoatlas/tree/master/src/main/java/ch/epfl/biop/atlas/aligner/command
        ImportImageCommand = jimport('ch.epfl.biop.atlas.aligner.command.ImportImageCommand')
        File = jimport('java.io.File')

        # Here we want to import images: check
        # https://github.com/BIOP/ijp-imagetoatlas/blob/master/src/main/java/ch/epfl/biop/atlas/aligner/command/ImportImageCommand.java

        FileArray = JArray(File)
        files = FileArray(len(filepaths))
        i = 0
        for filepath in filepaths:
            file = File(filepath)
            files[i] = file
            i = i + 1

        # Any missing input parameter will lead to a popup window asking the missing argument to the user
        return self.ij.command().run(ImportImageCommand, True, \
                                     "datasetname", JString('dataset'), \
                                     "files", files, \
                                     "mp", self.mp, \
                                     "split_rgb_channels", split_rgb, \
                                     "slice_axis_initial", z_location, \
                                     "increment_between_slices", z_increment \
                                     )

    def register_deepslice(self,
                           channels=[0],
                           allow_slicing_angle_change=True,
                           allow_change_slicing_position=True,
                           maintain_slices_order=True,
                           affine_transform=True
                           ):
        # TODO : add option  to rescale brightness/contrast in parameters
        if not self.atlas_name == 'Adult Mouse Brain - Allen Brain Atlas V3':
            print('Deep Slice only support the Allen Brain Atlas CCFv3 in coronal slicing mode')
            return

        if not self.slicing_mode == 'coronal':
            print('Deep Slice only support the Allen Brain Atlas CCFv3 in coronal slicing mode')
            return

        if not hasattr(self, 'run_deep_slice'):
            from abba.abba_private.DeepSliceProcessor import DeepSliceProcessor
            self.run_deep_slice = DeepSliceProcessor()

        RegistrationDeepSliceCommand = jimport('ch.epfl.biop.atlas.aligner.command.RegistrationDeepSliceCommand')

        # TODO : fix potential multiple running instance issues
        temp_folder = os.getcwd()+'/temp/deepslice/'

        # clean folder : remove all previous files
        for filename in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                # elif os.path.isdir(file_path):
                #    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # Any missing input parameter will lead to a popup window asking the missing argument to the user
        return self.ij.command().run(RegistrationDeepSliceCommand, True,
                                     "slices_string_channels", JString(''.join(map(str, channels))),
                                     "image_name_prefix", JString('Section'),
                                     "mp", self.mp,
                                     "allow_slicing_angle_change", allow_slicing_angle_change,
                                     "allow_change_slicing_position", allow_change_slicing_position,
                                     "maintain_slices_order", maintain_slices_order,
                                     "affine_transform", affine_transform,
                                     "deepSliceProcessor", self.run_deep_slice,
                                     "dataset_folder", JString(temp_folder)
                                     )
