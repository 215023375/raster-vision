#! /bin/bash

# Assuming conda environment name is 'rastervision-poc' as in the conda.env.yaml
CONDA_ENVIRONMENT_NAME=~/anaconda3/envs/rastervision-poc
ln -s $(pwd)/.conda/etc/conda/activate.d/update_ld_library_path.sh $CONDA_ENVIRONMENT_NAME/etc/conda/activate.d/
ln -s $(pwd)/.conda/etc/conda/deactivate.d/unset_ld_library_path.sh $CONDA_ENVIRONMENT_NAME/etc/conda/deactivate.d/
