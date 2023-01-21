#! /bin/bash

# Create $CONDA_PREFIX/lib64 dir (check if link exists)
[ ! -L "$CONDA_PREFIX"/lib64 ] && ln -s "$CONDA_PREFIX"/lib "$CONDA_PREFIX"/lib64

export _OLD_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"


# TODO: Create a separate script  for the PYTHONPATH (or rename this - and update symlink)
PROJECT_DIR="$HOME/workspace/lucc/submodules/raster-vision"
PYTHONPATH="$PROJECT_DIR/rastervision_customs:$PYTHONPATH"

export PYTHONPATH