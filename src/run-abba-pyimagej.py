# core dependencies
import time

# abba_python dependency
from abba_python import Abba
# in order to wait for a jvm shutdown
import jpype

if __name__ == '__main__':
    # -- FOR DEBUGGING
    # import imagej.doctor
    # imagej.doctor.checkup()
    # imagej.doctor.debug_to_stderr()

    # -- Atlas
    # Any brainglobe atlas can be used
    # show_atlases()
    # abba_python = Abba("azba_zfish_4um", slicing_mode='sagittal', headless=True)  # or any other brainglobe atlas

    # -- HEADLESS
    # abba_python = Abba('Adult Mouse Brain - Allen Brain Atlas V3', headless=True)  # or any other brainglobe atlas
    # --

    # -- NOT HEADLESS
    abba = Abba('Adult Mouse Brain - Allen Brain Atlas V3')
    abba.show_bdv_ui()  # creates and show a bdv view
    # --

    # everything will close 10 hours after the registration is done...
    # time.sleep(36000)  # Humm, because ij closes if the python process closes

    # Wait for the JVM to shut down
    while jpype.isJVMStarted():
        time.sleep(1)

    print("JVM has shut down")
