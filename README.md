# Perform misc operations on Digital models generated from LAS files
- Generate DxM from LAS point cloud files
- Extract values from a DxM along geometries

Note: DxM refers digital models in general (Digital xxx Model, that can be Digital Surface Model, Digital Terrain Model...)

Note: this project has only been tested on Linux

# Overview

## Main functionalities

###   Generate DxM from LAS point cloud files

This repo contains code to generate different kinds of digital models from LAS inputs:
 * DSM: digital surface model (model of the ground surface including natural and built features such as trees or buildings)
 * DTM: digital terrain model (model of the ground surface without natural and built features such as trees or buildings)
 * DHM: digital height model (model of the height of natural and built features from the ground)

### Extract values from a DxM along geometries
This repo contains also code to extract the minimum Z values along lines (defined in a geometry file) from raster containing Z value,  and clip them to the extent of polygons from another geometry file
The expected use case is : input lines are constraint lines used to open bridges in DTMs, clipping polygons are bridges under which the DTM should be opened

## Workflow
### Digital Models from LAS inputs

The overall workflow to create DXM from a classified LAS point cloud is:

As a preprocessing step, a buffer is added to each tile:
* buffer: add points from a buffer around the tile (from neighbor tiles) to limit border effects

This step can be mutualized when we generate several kinds of digital models.

To generate a Digital Terrain Model (DTM):
* interpolation : generate a DTM from the buffered point cloud. The point cloud is filtered (by classification) during the interpolation step

```
LAS -> buffer -> interpolation -> DTM
```

To generate a Digital Surface Model (DSM):
* interpolation : generate a DTM from the buffered point cloud. The point cloud is filtered (by classification) during the interpolation step

```
LAS -> buffer -> interpolation -> DSM
```

To generate a Digital Height Model (DHM):
* Compute a DSM and a DTM
* Compute DHM as DSM - DTM

```
DSM - DTM -> DHM
```

### Extract the minimum Z values along lines from raster containing Z value

The overall workflow to extract the minimum Z values along lines from MNS is:

- Create a VRT from a folder containing DxM
- Clip lines from geometry file to the raster extent
- Extract minimum Z value along each Line
- Clip lines to the extent of polygons (from another file)


## In this repo

This repo contains:
* code to compute the interpolation step on one tile
* code to compute the DHM from DSM and DTM on one tile
* scripts to compute the buffer step on one tile,
using the [ign-pdal-tools](http://gitlab.forge-idi.ign.fr/Lidar/pdalTools) library
* a script to run all steps together on a folder containing several tiles

## Interpolation

The selected interpolation method is: constrained Delaunay-based (CDT) TIN-linear

Steps are:
- filter the points to use in the interplation (using one dimension name and a list of values)
  (eg. Classification=2(ground) for a digital terrain model)
- triangulate the point cloud using Delaunay
- interpolate the height values at the center of the pixels using Faceraster
- write the result in a raster file.

During the interpolation step, a shapefile can be provided to mask polygons using a nodata value.

## Output format

**TODO**

# Installation

Install the conda environment for this repo using [mamba](https://github.com/mamba-org/mamba) (faster
reimplementation of conda):

```bash
make install
conda activate las_digital_models
```

The `run.sh` command uses `gnu-parallel` to implement multiprocessing.
To install it :

```bash
sudo apt install parallel
```

# Usage

The code in this repo can be executed either after being installed on your computer or via a
docker image (see the [Docker section](#docker) for this use case).

This code uses hydra to manage configuration and parameters. All configurations are available in
the `configs` folder.

##  Generate DxM from LAS point cloud files

> **Warning** In all steps, the tiles are supposed to be named following this syntax:
> `prefix1_prefix2_{coord_x}_{coord_y}_suffix` where
> `coord_x` and `coord_y` are the coordinates of the top-left corner of the tile.
> By default, they are given in km, and the tile width is 1km. Otherwise, you must override the
> values of `tile_geometry.tile_width` and `tile_geometry.tile_coord_scale`
> * `tile_geometry.tile_width` must contain the tile size in meters
> * `tile_geometry.tile_coord_scale` must contain the `coord_x` and `coord_y` scale so that `coord_{x or y} * tile_geometry.tile_coord_scale` are the coordinates of the top-left corner in meters

### Whole pipeline

To run the whole pipeline (DSM + DTM + DHM) on all the LAS files in a folder, use `run.sh`.

```bash
./run.sh -i INPUT_DIR -o OUTPUT_DIR -p PIXEL_SIZE -j PARALLEL_JOBS -s SHAPEFILE
```

with:
* INPUT_DIR: folder that contains the input point clouds
* OUTPUT_DIR: folder where the output will be saved
* PIXEL_SIZE: The desired pixel size of the output (in meters)
* PARALLEL_JOBS: the number of jobs to run in parallel, 0 is as many as possible (cf. parallel command)
* SHAPEFILE: a shapefile containing a mask to hide data from specific areas (the masked areas will contain no-data values)

It will generate:
* Temporary files (you can delete them manually when the result looks good):
  * ${OUTPUT_DIR}/buffer : buffered las for DTM and DSM generation
* Output folders:
  * ${OUTPUT_DIR}/DTM###   Generate DxM from LAS point cloud files
  * ${OUTPUT_DIR}/DSM
  * ${OUTPUT_DIR}/DHM

### Buffer

To add a buffer to a point cloud using `ign-pdal-tools`:

```bash
python -m las_digital_models.filter_one_tile \
  io.input_dir=INPUT_DIR \
  io.input_filename=INPUT_FILENAME \
  io.output_dir=OUTPUT_DIR \
  buffer.size=10
```

Any other parameter in the `./configs` tree can be overriden in the command (see the doc of
[hydra](https://hydra.cc/) for more details on usage)

### Interpolation

To run interpolation (DXM generation):

```bash
python -m las_digital_models.ip_one_tile \
    io.input_dir=${BUFFERED_DIR} \
    io.input_filename={} \
    io.output_dir=${DXM_DIR} \
    tile_geometry.pixel_size=${PIXEL_SIZE} \
    filter.dimension="Classification" \
    filter.keep_values=[2,66]
```

`filter.keep_values` must be a list inside `[]`, separated by `,` without spaces.

Any other parameter in the `./configs` tree can be overriden in the command (see the doc of
[hydra](https://hydra.cc/) for more details on usage)

During the interpolation step, a shapefile can be provided to mask polygons using `tile_geometry.no_data_value`.
To use it, provide the shapefile path with the `io.no_data_mask_shapefile` argument.

### DHM

To generate DHM:
```bash
    python -m las_digital_models.dhm_one_tile \
        dhm.input_dsm_dir=${DSM_DIR} \
        dhm.input_dtm_dir=${DTM_DIR} \
        io.input_filename={} \
        io.output_dir=${DHM_DIR} \
        tile_geometry.pixel_size=${PIXEL_SIZE}

```
`dhm.input_dsm_dir` and `dhm.input_dtm_dir` must contained DSM and DTM generated with
`las_digital_models.ip_one_tile` using the same pixel_size as given in
arguments.

Any other parameter in the `./configs` tree can be overriden in the command (see the doc of
[hydra](https://hydra.cc/) for more details on usage)



## Extract values from a DxM along geometries

### Extract the minimum Z values

with:
* INPUT_RASTER_DIR: folder that contains the raster
* INPUT_GEOMETRY_DIR: folder that contains the constraints lines (lines)
* INPUT_CLIP_GEOMETRY_DIR: folder that contains the clipping geometries
* INPUT_GEOMETRY_FILENAME: Name of geometry that contains the "input geometry".
* INPUT_CLIP_GEOMETRY_FILENAME: Name of geometry to use for clipping the "input geometry" after minZ is extracted.
* OUTPUT_DIR: folder where the output will be saved
* OUTPUT_VRT_FILENAME: Name of VRT file
* OUTPUT_GEOMETRY_FILENAME: Name og geometry that contains the "output geoemtry"

To run extraction of minimum Z value :

```bash
    python -m las_digital_models.extract_stat_from_raster.extract_z_virtual_lines_from_raster \
        extract_stat.input_raster_dir=${INPUT_RASTER_DIR} \
        extract_stat.input_geometry_dir=${INPUT_GEOMETRY_DIR} \
        extract_stat.input_clip_geometry_dir=${INPUT_CLIP_GEOMETRY_DIR} \
        extract_stat.input_geometry_filename=${INPUT_GEOMETRY_FILENAME} \
        extract_stat.input_clip_geometry_filename=${INPUT_CLIP_GEOMETRY_FILENAME} \
        extract_stat.output_vrt_filename=${OUTPUT_VRT_FILENAME} \
        extract_stat.output_dir=${OUTPUT_DIR} \
        extract_stat.output_geometry_filename=${OUTPUT_GEOMETRY_FILENAME}
```

Any other parameter in the `./configs` tree can be overriden in the command (see the doc of
[hydra](https://hydra.cc/) for more details on usage)



# Docker

This codebase can be used in a docker image.

To generate the docker image, run `make docker-build`

To deploy it on nexus, run `make docker-deploy`

To run interpolation:
```bash
# Example for interpolation
docker run -t --rm --userns=host --shm-size=2gb \
    -v $INPUT_DIR:/input
    -v $OUTPUT_DIR:/output
    lidar_hd/las_digital_models:$VERSION
    python -m las_digital_models.ip_one_tile \
        io.input_dir=/input \
        io.input_filename=$FILENAME \
        io.output_dir=/output \
        tile_geometry.pixel_size=$PIXEL_SIZE
```

The version number can be retrieved with `python -m las_digital_models.version`


# Build and deploy as python package

## Build the library

```
make build
```

## Deploy on IGN's Nexus

```
make deploy
```

# A word of caution

If you are using an Anaconda virtual environment for PDAL/CGAL, you should first activate the environment in Anaconda prompt and _then_ run the relevant script
from the same prompt. So, for example:
1. Create conda environment : `conda env create -n las_digital_models -f environment.yml`
2. Activate conda environment : `conda activate las_digital_models`
2. Launch the module : `python -m [name of the module to run] [argument_1] [argument_2] [...]`

Another word of caution with the outputs is that they all use a fixed no-data value of -9999. This includes the GeoTIFF exporter. To view the results correctly, you should keep in mind that while the upper bounds of the data will be determined correctly by the viewer software (e.g. QGIS), the lower bound will be -9999.

**Note:** ASC export is not currently supported for the PDAL-IDW algorithm.

**Another note:** You are advised to configure the IDWquad parametrisation **with performance in mind** when first getting started. Otherwise it might take _veeeeeery long_ to finish.
