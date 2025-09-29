#!/bin/bash

# Break if command fails
set -e

INPUT="/input/"
OUTPUT="/output/"
PIXEL_SIZE=0.5
PARALLEL_JOBS=0
CPU_LIMIT=-1
SHAPEFILE=""

SOURCE_DIR=$(dirname ${BASH_SOURCE[0]})
CONFIG_NAME="config"

USAGE="""
Usage ./run.sh -i INPUT_DIR -o OUTPUT_DIR -p PIXEL_SIZE -j PARALLEL_JOBS -s SHAPEFILE -c CONFIG_NAME\n
For PARALLEL_JOBS, 0 is : use as many as possible (cf. parallel command)\n
CONFIG_NAME (for test use only: override default hydra config)
"""
# Parse arguments in order to possibly overwrite paths
while getopts "h?i:o:p:j:s:c:" opt; do
  case "$opt" in
    h|\?)
      echo -e ${USAGE}
      exit 0
      ;;
    i)  INPUT=${OPTARG}
      ;;
    o)  OUTPUT=${OPTARG}
      ;;
    p)  PIXEL_SIZE=${OPTARG}
      ;;
    j)  PARALLEL_JOBS=${OPTARG}
      ;;
    s) SHAPEFILE=${OPTARG}
      ;;
    c) CONFIG_NAME=${OPTARG}
      ;;
  esac
done

# Get all filenames for las or laz files in input folder
#    sed 's/^\.\///g' : remove ./ at beginning of file
FILENAMES=($(cd ${INPUT} && find .  -maxdepth 1 -type f \( -iname \*.las -o -iname \*.laz \) | sed 's/^\.\///g' ))


echo "GENERATE DSM/DTM/DHM ON ${#FILENAMES[@]} FILES"
echo ""

parallel --jobs ${PARALLEL_JOBS} \
    python -m las_digital_models.main \
        --config-name=${CONFIG_NAME} \
        io.input_dir=${INPUT} \
        io.input_filename={} \
        io.output_dir=${OUTPUT} \
        tile_geometry.pixel_size=${PIXEL_SIZE} \
        io.no_data_mask_shapefile=${SHAPEFILE} \
        ::: "${FILENAMES[@]}"

