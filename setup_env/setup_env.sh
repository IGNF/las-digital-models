#!/bin/bash

# Be sure that you are using last pip version
# by running pip install --upgrade pip

# Run this from a bash using
# source setup_env/setup_env.sh


conda env create -n produit_derive_lidar -f environment.yml --force
conda activate produit_derive_lidar
