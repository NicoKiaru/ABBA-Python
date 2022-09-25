from scyjava import jimport
from jpype import JImplements, JOverride
from jpype.types import JString, JDouble, JInt, JArray
from abba.abba_private import AbbaOntology, AbbaMap
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