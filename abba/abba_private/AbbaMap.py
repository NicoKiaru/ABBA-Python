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