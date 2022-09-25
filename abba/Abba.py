from scyjava import jimport
from jpype import JImplements, JOverride
from jpype.types import JString, JDouble, JInt, JArray
import numpy as np

#def import_java_classes():
#global AffineTransform3D, ArrayList, Atlas, AtlasHelper, AtlasMap, AtlasNode, AtlasOntology, BdvFunctions, BdvOptions

AffineTransform3D = jimport('net.imglib2.realtransform.AffineTransform3D')
ArrayList = jimport('java.util.ArrayList')
Atlas = jimport('ch.epfl.biop.atlas.struct.Atlas')
AtlasHelper = jimport('ch.epfl.biop.atlas.struct.AtlasHelper')
AtlasMap = jimport('ch.epfl.biop.atlas.struct.AtlasMap')
AtlasNode = jimport('ch.epfl.biop.atlas.struct.AtlasNode')
AtlasOntology = jimport('ch.epfl.biop.atlas.struct.AtlasOntology')
BdvFunctions = jimport('bdv.util.BdvFunctions')
BdvOptions = jimport('bdv.util.BdvOptions')

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
        ij,
        slicing_mode = 'coronal' # or sagittal or horizontal
    ):
        # Initialising ImageJ, if not already initialised
        # Makes the atlas object
        self.atlas = atlas
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


@JImplements(Atlas)
class AbbaAtlas(object):

    def __init__(self, bg_atlas, ij):
        self.atlas = bg_atlas
        self.ij = ij

    @JOverride
    def getMap(self):
        return self.bg_atlasmap

    @JOverride
    def getOntology(self):
        return self.bg_ontology

    @JOverride
    def initialize(self, mapURL, ontologyURL):
        self.bg_ontology = AbbaOntology(self.atlas)
        self.bg_ontology.initialize()
        self.bg_ontology.setNamingProperty(JString('acronym'))
        self.bg_atlasmap = AbbaMap(self.atlas, self.ij)
        self.bg_atlasmap.initialize(self.atlas.atlas_name)
        self.dois = ArrayList()
        self.dois.add(JString('doi1'))  # TODO
        self.dois.add(JString('doi2'))

    @JOverride
    def getDOIs(self):
        return self.dois

    @JOverride
    def getURL(self):
        return JString('BrainGlobe Atlas URL...')

    @JOverride
    def getName(self):
        return JString(self.atlas.atlas_name)

    @JOverride
    def toString(self):
        return self.getName()

@JImplements(AtlasOntology)
class AbbaOntology(object):

    def __init__(self, bg_atlas):
        self.atlas = bg_atlas

    @JOverride
    def getName(self):
        return JString(self.atlas.atlas_name)

    @JOverride
    def initialize(self):
        self.root_node = AbbaAtlasNode(self.atlas, self.atlas.structures.tree.root, None)
        self.idToAtlasNodeMap = AtlasHelper.buildIdToAtlasNodeMap(self.root_node)

    @JOverride
    def setDataSource(self, dataSource):
        self.dataSource = dataSource

    @JOverride
    def getDataSource(self):
        return self.dataSource  # return URL

    @JOverride
    def getRoot(self):
        return self.root_node  # return AtlasNode

    @JOverride
    def getNodeFromId(self, index):
        return self.idToAtlasNodeMap.get(index)  # return AtlasNode

    @JOverride
    def getNamingProperty(self):
        return self.namingProperty

    @JOverride
    def setNamingProperty(self, namingProperty):
        self.namingProperty = namingProperty

@JImplements(AtlasMap)
class AbbaMap(object):

    def __init__(self, bg_atlas, ij):
        # this function is called way too many times if I put here the content
        # of initialize... and I don't know why
        # that's why there's this initialize function
        self.atlas = bg_atlas
        self.ij = ij

    @JOverride
    def setDataSource(self, dataSource):
        self.dataSource = dataSource

    @JOverride
    def initialize(self, atlasName):
        self.atlasName = str(atlasName)

        atlas_resolution_in__mm = JDouble(min(self.atlas.metadata['resolution']) / 1000.0)

        vox_x_mm = self.atlas.metadata['resolution'][0] / 1000.0
        vox_y_mm = self.atlas.metadata['resolution'][1] / 1000.0
        vox_z_mm = self.atlas.metadata['resolution'][2] / 1000.0

        affine_transform = AffineTransform3D()
        affine_transform.scale(JDouble(vox_x_mm), JDouble(vox_y_mm), JDouble(vox_z_mm))

        # Convert
        bss = BdvFunctions.show(self.ij.py.to_java(self.atlas.reference), JString(self.atlas.atlas_name + '_reference'),
                                BdvOptions.options().sourceTransform(affine_transform))
        reference_sac = bss.getSources().get(0)
        bss.getBdvHandle().close()

        bss = BdvFunctions.show(self.ij.py.to_java(self.atlas.hemispheres), JString(self.atlas.atlas_name + '_hemispheres'),
                                BdvOptions.options().sourceTransform(affine_transform))
        left_right_sac = bss.getSources().get(0)
        bss.getBdvHandle().close()

        bss = BdvFunctions.show(self.ij.py.to_java(self.atlas.annotation), JString(self.atlas.atlas_name + '_annotation'),
                                BdvOptions.options().sourceTransform(affine_transform))
        self.annotation_sac = bss.getSources().get(0)
        bss.getBdvHandle().close()

        image_keys = ArrayList()
        image_keys.add(JString('reference'))
        image_keys.add(JString('X'))
        image_keys.add(JString('Y'))
        image_keys.add(JString('Z'))
        image_keys.add(JString('Left Right'))

        structural_images = {
            'reference': reference_sac,
            'X': AtlasHelper.getCoordinateSac(0, JString('X')),
            'Y': AtlasHelper.getCoordinateSac(1, JString('Y')),
            'Z': AtlasHelper.getCoordinateSac(2, JString('Z')),
            'Left Right': left_right_sac
        }  # return Map<String,SourceAndConverter>

        self.atlas_resolution_in__mm = atlas_resolution_in__mm
        self.affine_transform = affine_transform
        self.image_keys = image_keys
        self.structural_images = structural_images
        self.maxReference = JDouble(np.max(self.atlas.reference) * 2)

    @JOverride
    def getDataSource(self):
        return self.dataSource  # return URL

    @JOverride
    def getStructuralImages(self):
        return self.structural_images

    @JOverride
    def getImagesKeys(self):
        return self.image_keys

    @JOverride
    def getLabelImage(self):
        return self.annotation_sac  # SourceAndConverter

    @JOverride
    def getAtlasPrecisionInMillimeter(self):
        return self.atlas_resolution_in__mm

    @JOverride
    def getCoronalTransform(self):
        return AffineTransform3D()

    @JOverride
    def getImageMax(self, key):
        return self.maxReference  # double

    @JOverride
    def labelRight(self):
        return JInt(1)

    @JOverride
    def labelLeft(self):
        return JInt(2)

@JImplements(AtlasNode)
class AbbaAtlasNode(object):

    def __init__(self, bg_atlas, index, parent_node):
        self.atlas = bg_atlas
        self.id = index
        self.parent_node = parent_node
        children_nodes = []
        for child in bg_atlas.structures.tree.children(index):
            childNode = AbbaAtlasNode(bg_atlas, child.identifier, self)
            children_nodes.append(childNode)
        self.children_nodes = ArrayList(children_nodes)
        self.namingKey = JString('acronym')

    @JOverride
    def getId(self):
        return JInt(self.id)

    @JOverride
    def getColor(self):
        val = JInt[4]
        rgb = self.data().get('rgb_triplet')
        return val

    @JOverride
    def data(self):
        dict_ori = self.atlas.structures[self.id]
        string_dict = {}
        for key in dict_ori.keys():
            try:
                string_dict[key] = JString(str(dict_ori[key]))
            except Exception:
                pass
        return string_dict  # self.atlas.structures[self.id] #string_dict #self.atlas.structures[self.id] # issue with map

    @JOverride
    def parent(self):
        return self.parent_node

    @JOverride
    def children(self):
        return self.children_nodes

    @JOverride
    def toString(self):
        return self.data().get(self.namingKey)