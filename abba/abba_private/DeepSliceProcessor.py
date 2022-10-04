from scyjava import jimport
from deepslice.DeepSlice import DeepSlice
from jpype import JImplements, JOverride
from jpype.types import JString
import os

import urllib.request
from tqdm import tqdm
from deepslice.DeepSlice import get_deepslice_path

# Import deepslice and make the function for the ABBA command
Function = jimport('java.util.function.Function')
File = jimport('java.io.File')


# ----- Download with progress bar, cf https://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


# ------------

def check_model_is_present():
    path_to_model = get_deepslice_path() + "/NN_weights"
    if not os.path.isdir(path_to_model):
        print('DeepSlice model not present, 240 Mb will be downloaded ')
        os.mkdir(path_to_model)
    model_files = ['/Allen_Mixed_Best.h5',
                   '/Synthetic_data_final.hdf5',
                   '/xception_weights_tf_dim_ordering_tf_kernels.h5']

    deepslice_model_url = 'https://github.com/PolarBean/DeepSlice/raw/master/NN_weights'

    for file in model_files:
        if not os.path.exists(path_to_model + file):
            target_url = deepslice_model_url + file
            print('Missing DeepSlice model file ' + file + '. Downloading (80Mb)...')
            download_url(target_url, path_to_model + file)


@JImplements(Function)
class DeepSliceProcessor:

    @JOverride
    def apply(self, folder):
        check_model_is_present()
        model = DeepSlice()
        model.Build()
        model.predict(image_dir=str(folder.getParent()))
        out = File(folder, JString('results'))
        model.Save_Results(out.getAbsolutePath())
        return File(folder, JString('results.xml'))
