#! /bin/bash

[ -L "$CONDA_PREFIX"/lib64 ] && rm "$CONDA_PREFIX"/lib64

export LD_LIBRARY_PATH=$_OLD_LD_LIBRARY_PATH
unset _OLD_LD_LIBRARY_PATH

