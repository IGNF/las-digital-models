#!/bin/bash

# Break if command fails
set -e

INPUT="/input/"
OUTPUT="/output/"
PIXEL_SIZE=0.5
PARALLEL_JOBS=0
CPU_LIMIT=-1

SOURCE_DIR=$(dirname ${BASH_SOURCE[0]})

USAGE="""
Usage ./run.sh -i INPUT_DIR -o OUTPUT_DIR -p PIXEL_SIZE -j PARALLEL_JOBS \n
For PARALLEL_JOBS, 0 is : use as many as possible (cf. parallel command)
"""
# Parse arguments in order to possibly overwrite paths
while getopts "h?i:o:p:c:" opt; do
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
    c)  CPU_LIMIT=${OPTARG}
      ;;
  esac
done

# Get existing methods from config directory
# sed commands:
#    sed 's/^\.\///g' : remove ./ at beginning of file
#    sed -n 's/\.yaml$//p'' : remove .yaml at end of file
METHODS=($(cd ${SOURCE_DIR}/configs/interpolation && find .  -maxdepth 1 -type f | sed 's/^\.\///g' | sed -n 's/\.yaml$//p'))

# Get all filenames for las or laz files in input folder
#    sed 's/^\.\///g' : remove ./ at beginning of file
FILENAMES=($(cd ${INPUT} && find .  -maxdepth 1 -type f \( -iname \*.las -o -iname \*.laz \) | sed 's/^\.\///g' ))


echo "GENERATE DSM/DTM/DHM FOR METHODS: ${METHODS[@]} ON ${#FILENAMES[@]} FILES"
echo ""

echo "------------------"
echo "RUN DTM GENERATION"
echo "------------------"

# Output filenames for each step
FILTERED_DIR=${OUTPUT}/ground
BUFFERED_DIR=${OUTPUT}/ground_with_buffer
DTM_DIR=${OUTPUT}/DTM

# Step 1.1 : filter ground
echo "------------------"
echo "filter ground"
echo "------------------"
parallel --jobs ${PARALLEL_JOBS} \
    python -m produit_derive_lidar.filter_one_tile \
        io.input_dir=${INPUT} \
        io.input_filename={} \
        io.output_dir=${FILTERED_DIR} \
        "filter.keep_classes=[2,9,66]" \
        ::: "${FILENAMES[@]}"


# Step 1.2: Create las with buffer from its neighbors tiles
# /!\ rasters generated from these las tiles will need to be cropped to match the input las area
echo "------------------"
echo "add buffer"
echo "------------------"
parallel --jobs ${PARALLEL_JOBS} \
    python -m produit_derive_lidar.add_buffer_one_tile \
        io.input_dir=${FILTERED_DIR} \
        io.input_filename={} \
        io.output_dir=${BUFFERED_DIR} \
        ::: "${FILENAMES[@]}"


# Step 1.3 ; create DTM with the severals method
echo "------------------"
echo "interpolation"
echo "------------------"
for METHOD in ${METHODS[@]}
do
  parallel --jobs ${PARALLEL_JOBS} \
      python -m produit_derive_lidar.ip_one_tile \
          io.input_dir=${BUFFERED_DIR} \
          io.input_filename={} \
          io.output_dir=${DTM_DIR} \
          interpolation=${METHOD} \
          tile_geometry.pixel_size=${PIXEL_SIZE} \
          ::: "${FILENAMES[@]}"
done


echo "------------------"
echo "RUN DSM GENERATION"
echo "------------------"


# Output filenames for each step
FILTERED_DIR=${OUTPUT}/upground
BUFFERED_DIR=${OUTPUT}/upground_with_buffer
DSM_DIR=${OUTPUT}/DSM

# Step 2.1 : filter ground + upground
parallel --jobs ${PARALLEL_JOBS} \
    python -m produit_derive_lidar.filter_one_tile \
        io.input_dir=${INPUT} \
        io.input_filename={} \
        io.output_dir=${FILTERED_DIR} \
        "filter.keep_classes=[2,3,4,5,6,9,17]" \
        ::: "${FILENAMES[@]}"

# Step 2.2: Create las with buffer from its neighbors tiles
#/!\ rasters generated from these las tiles will need to be cropped to match the input las area
parallel --jobs ${PARALLEL_JOBS} \
    python -m produit_derive_lidar.add_buffer_one_tile \
        io.input_dir=${FILTERED_DIR} \
        io.input_filename={} \
        io.output_dir=${BUFFERED_DIR} \
        ::: "${FILENAMES[@]}"

# # Step 2.3 ; create DTM with the severals method
for METHOD in ${METHODS[@]}
do
  parallel --jobs ${PARALLEL_JOBS} \
      python -m produit_derive_lidar.ip_one_tile \
          io.input_dir=${BUFFERED_DIR} \
          io.input_filename={} \
          io.output_dir=${DSM_DIR} \
          interpolation=${METHOD} \
          tile_geometry.pixel_size=${PIXEL_SIZE} \
          ::: "${FILENAMES[@]}"
done

echo "------------------"
echo "RUN DHM GENERATION"
echo "------------------"


# # Step 4 ; create DHM with the severals method
# Output filenames for each step
DHM_DIR=${OUTPUT}/DHM

for METHOD in ${METHODS[@]}
do
parallel --jobs ${PARALLEL_JOBS} \
    python -m produit_derive_lidar.dhm_one_tile \
        dhm.input_dsm_dir=${DSM_DIR} \
        dhm.input_dtm_dir=${DTM_DIR} \
        io.input_filename={} \
        io.output_dir=${DHM_DIR} \
        interpolation=${METHOD} \
        tile_geometry.pixel_size=${PIXEL_SIZE} \
        ::: "${FILENAMES[@]}"
done