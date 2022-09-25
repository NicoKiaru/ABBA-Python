from scyjava import jimport
from jpype.types import JString, JArray
import imagej



class Abba:
    """Add remote atlas fetching and version comparison functionalities
    to the core Atlas class.
    Parameters
    ----------
    atlas_name : str
        Name of the atlas to be used, should be available in BrainGlobe
    ij : undef
        ImageJ instance, should be reused if you need to open several ABBA instances
    """

    def __init__(
        self,
        atlas,
        ij=None,
        slicing_mode = 'coronal' # or sagittal or horizontal
    ):
        if ij is None:
            imagej_core_dep = 'net.imagej:imagej:2.9.0'
            imagej_legacy_dep = 'net.imagej:imagej-legacy:0.39.2'
            abba_dep = 'ch.epfl.biop:ImageToAtlasRegister:0.3.3'
            deps_pack = [imagej_core_dep, imagej_legacy_dep, abba_dep]
            ij = imagej.init(deps_pack, mode='interactive')
            self.ij = ij

        # Initialising ImageJ, if not already initialised
        # Makes the atlas object
        self.atlas = atlas
        from abba.abba_private import AbbaAtlas
        self.convertedAtlas = AbbaAtlas(self.atlas, ij)
        self.convertedAtlas.initialize(None, None)

        # Starts ABBA
        # Puts it in the scijava ObjectService for automatic discovery if necessary
        ij.object().addObject(self.convertedAtlas)

        self.slicing_mode = slicing_mode

        # .. but before : logger, please shut up
        DebugTools = jimport('loci.common.DebugTools')
        DebugTools.enableLogging('DEBUG')

        # Ok, let's create abba's model: mp = multipositioner

        ABBAStartCommand = jimport('ch.epfl.biop.atlas.aligner.command.ABBAStartCommand')  # Command import
        self.mp = ij.command().run(ABBAStartCommand, True,
                         'slicing_mode',self.slicing_mode,
                         'ba', self.convertedAtlas).get().getOutput('mp')

    def ij(self):
        return self.ij

    def show_bdv_ui(self):
        if not hasattr(self, 'bdv_view'):
            print("no bdv view")
            SourceAndConverterServices = jimport('sc.fiji.bdvpg.services.SourceAndConverterServices')
            BdvMultislicePositionerView = jimport('ch.epfl.biop.atlas.aligner.gui.bdv.BdvMultislicePositionerView')
            bdvh = SourceAndConverterServices.getBdvDisplayService().getNewBdv()
            self.bdv_view = BdvMultislicePositionerView(self.mp, bdvh)
        else:
            # TODO: make sure it is visible
            pass

    def add_files(self, z_location = 0, z_increment = 0.02, split_rgb = False, *filepaths):
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
            i = i+1

        # Any missing input parameter will lead to a popup window asking the missing argument to the user
        self.ij.command().run(ImportImageCommand, True, \
                         "datasetname", JString('dataset'), \
                         "files", files, \
                         "mp", self.mp, \
                         "split_rgb_channels", split_rgb, \
                         "slice_axis_initial", z_location, \
                         "increment_between_slices", z_increment \
                         )
