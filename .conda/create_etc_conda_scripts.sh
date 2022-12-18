#! /bin/bash

ln -s $(pwd)/.conda/etc/conda/activate.d/update_ld_library_path.sh $CONDA_PREFIX/etc/conda/activate.d/
ln -s $(pwd)/.conda/etc/conda/deactivate.d/unset_ld_library_path.sh $CONDA_PREFIX/etc/conda/deactivate.d/
