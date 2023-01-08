from scyjava import jimport
from jpype import JImplements, JOverride
from jpype.types import JString, JInt

ArrayList = jimport('java.util.ArrayList')
AtlasNode = jimport('ch.epfl.biop.atlas.struct.AtlasNode')


@JImplements(AtlasNode)
class AbbaAtlasNode(object):
    """This python class is part of the translation mechanism between the underlying Java ABBA API:
    https://github.com/BIOP/ijp-atlas/tree/main/src/main/java/ch/epfl/biop/atlas/struct
    and the BrainGlobe API:
    https://github.com/brainglobe/bg-atlasapi/

    Wrapper inner class that implements the following Java interface:
    https://github.com/BIOP/ijp-atlas/blob/main/src/main/java/ch/epfl/biop/atlas/struct/AtlasNode.java
    """

    def __init__(self, bg_atlas, index, parent_node):
        self.atlas = bg_atlas
        self.id = index
        self.parent_node = parent_node
        children_nodes = []
        for child in bg_atlas.structures.tree.children(index):
            child_node = AbbaAtlasNode(bg_atlas, child.identifier, self)
            children_nodes.append(child_node)
        self.children_nodes = ArrayList(children_nodes)
        self.namingKey = JString('acronym')
        dict_ori = self.atlas.structures[self.id]
        #  TODO : IMPROVE ABSOLUTELY ABYSMAL PERFORMANCE OF THE CODE BELOW
        string_dict = {}
        for key in dict_ori.keys():
            try:
                string_dict[key] = JString(str(dict_ori[key]))
            except Exception:
                pass
        self._data = string_dict
        self._to_string = self._data.get(self.namingKey)
        self._id = JInt(self.id)
        val = JInt[4]
        val[0] = JInt(dict_ori['rgb_triplet'][0])
        val[1] = JInt(dict_ori['rgb_triplet'][1])
        val[2] = JInt(dict_ori['rgb_triplet'][2])
        val[3] = JInt(255)
        self._color = val

    @JOverride
    def getId(self):
        return self._id

    @JOverride
    def getColor(self):
        return self._color

    @JOverride
    def data(self):
        return self._data

    @JOverride
    def parent(self):
        return self.parent_node

    @JOverride
    def children(self):
        return self.children_nodes

    @JOverride
    def toString(self):
        return self._to_string
