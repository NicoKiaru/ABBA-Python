# core dependencies
import time

from abba_python.Abba import enable_python_hooks, get_java_dependencies, add_brainglobe_atlases
# abba_python dependency
from abba_python import Abba
# in order to wait for a jvm shutdown
import jpype
import imagej

import os
import ctypes


if __name__ == '__main__':

    # MAC ISSUE
    # https: // github.com / imagej / pyimagej / issues / 23
    # -- FOR DEBUGGING
    # import imagej.doctor
    # imagej.doctor.checkup()
    # imagej.doctor.debug_to_stderr()
    # Set jgo dir: https://github.com/scijava/jgo#usage
    # -- Atlas
    # Any brainglobe atlas can be used
    # show_atlases()
    # abba_python = Abba("azba_zfish_4um", slicing_mode='sagittal', headless=True)  # or any other brainglobe atlas

    # -- HEADLESS
    # abba_python = Abba('Adult Mouse Brain - Allen Brain Atlas V3', headless=True)  # or any other brainglobe atlas
    # --

    # -- NOT HEADLESS
    # abba = Abba('Adult Mouse Brain - Allen Brain Atlas V3')
    # abba.show_bdv_ui()  # creates and show a bdv view
    ij = imagej.init(get_java_dependencies(), mode="interactive")
    ij.ui().showUI()
    enable_python_hooks(ij)
    add_brainglobe_atlases(ij)

    # Set Elastix Path:
    # File ch.epfl.biop.wrappers.elastix.Elastix exePath
    # File ch.epfl.biop.wrappers.transformix.Transformix exePath
    from scyjava import jimport
    from jpype.types import JString

    # loci.common.DebugTools.enableLogging("OFF");
    DebugTools = jimport('loci.common.DebugTools')
    DebugTools.enableLogging('OFF')

    import platform
    if platform.system() == 'Windows':
        elastixPath = str(os.path.join(os.getcwd(), 'elastix-5.0.1-win64', 'elastix.exe'))
        transformixPath = str(os.path.join(os.getcwd(), 'elastix-5.0.1-win64', 'transformix.exe'))
        # transformixPath = str(os.path.join(os.path.dirname(os.getcwd()), 'elastix-5.0.1-win64', 'transformix.exe'))

        Elastix = jimport('ch.epfl.biop.wrappers.elastix.Elastix')
        Elastix.exePath = JString(str(elastixPath))
        Transformix = jimport('ch.epfl.biop.wrappers.transformix.Transformix')
        Transformix.exePath = JString(str(transformixPath))

        # Now let's set the atlas folder location in a folder with all users access

        AtlasLocationHelper = jimport('ch.epfl.biop.atlas.AtlasLocationHelper')
        directory = os.path.join(os.environ['ProgramData'], 'abba-atlas')

        # create the directory with write access for all users
        try:
            print('Attempt to set ABBA Atlas cache directory to ' + directory)
            # //os.mkdir(directory)
            os.makedirs(directory, exist_ok=True)

            # Set directory permissions for all users
            # p = ctypes.windll.kernel32.SetFileSecurityW(directory, 1, ctypes.c_void_p(0))
            # if not p:
            #    raise ctypes.WinError()
            # else:
            atlasPath = str(directory)
            File = jimport('java.io.File')
            AtlasLocationHelper.defaultCacheDir = File(JString(atlasPath))
            print('ABBA Atlas cache directory set to ' + directory)
        except OSError:
            print('ERROR! Could not set ABBA Atlas cache dir')
            # directory already exists
            pass



    # --

    # Wait for the JVM to shut down
    while jpype.isJVMStarted():
        time.sleep(1)

    print("JVM has shut down")
