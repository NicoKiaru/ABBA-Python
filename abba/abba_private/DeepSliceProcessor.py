from scyjava import jimport
from deepslice.DeepSlice import DeepSlice
from jpype import JImplements, JOverride
from jpype.types import JString

# Import deepslice and make the function for the ABBA command
Function = jimport('java.util.function.Function')
File = jimport('java.io.File')

@JImplements(Function)
class DeepSliceProcessor:
    @JOverride
    def apply(self,folder):
        Model = DeepSlice()
        Model.Build()
        print(folder.getParent())
        Model.predict('deepslice')#str(folder.getParent()))
        out = File(folder,JString('results'))
        print(out.getAbsolutePath())
        Model.Save_Results(out.getAbsolutePath())
        return File(folder,JString('results.xml'))