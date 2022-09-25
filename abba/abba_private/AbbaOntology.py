from scyjava import jimport
from jpype import JImplements, JOverride
from jpype.types import JString, JDouble, JInt, JArray

import numpy as np

from abba.abba_private import AbbaAtlasNode

AffineTransform3D = jimport('net.imglib2.realtransform.AffineTransform3D')
ArrayList = jimport('java.util.ArrayList')
Atlas = jimport('ch.epfl.biop.atlas.struct.Atlas')
AtlasHelper = jimport('ch.epfl.biop.atlas.struct.AtlasHelper')
AtlasMap = jimport('ch.epfl.biop.atlas.struct.AtlasMap')
AtlasNode = jimport('ch.epfl.biop.atlas.struct.AtlasNode')
AtlasOntology = jimport('ch.epfl.biop.atlas.struct.AtlasOntology')
BdvFunctions = jimport('bdv.util.BdvFunctions')
BdvOptions = jimport('bdv.util.BdvOptions')




@JImplements(AtlasOntology)
class AbbaOntology(object):

    def __init__(self, bg_atlas):
        self.atlas = bg_atlas

    @JOverride
    def getName(self):
        return JString(self.atlas.atlas_name)

    @JOverride
    def initialize(self):
        self.root_node = AbbaAtlasNode.AbbaAtlasNode(self.atlas, self.atlas.structures.tree.root, None)
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