from scyjava import jimport
from jpype import JImplements, JOverride
from jpype.types import JString, JDouble, JInt, JArray

import numpy as np

AffineTransform3D = jimport('net.imglib2.realtransform.AffineTransform3D')
ArrayList = jimport('java.util.ArrayList')
Atlas = jimport('ch.epfl.biop.atlas.struct.Atlas')
AtlasHelper = jimport('ch.epfl.biop.atlas.struct.AtlasHelper')
AtlasMap = jimport('ch.epfl.biop.atlas.struct.AtlasMap')
AtlasNode = jimport('ch.epfl.biop.atlas.struct.AtlasNode')
AtlasOntology = jimport('ch.epfl.biop.atlas.struct.AtlasOntology')
BdvFunctions = jimport('bdv.util.BdvFunctions')
BdvOptions = jimport('bdv.util.BdvOptions')



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