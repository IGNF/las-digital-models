# Generate DXM from LAS point cloud files
This repo contains code to generate different kinds of digital models from LAS inputs:
* DSM: digital surface model (model of the ground surface including natural and built features such as trees or buildings)
* DTM: digital terrain model (model of the ground surface without natural and built features such as trees or buildings)
* DHM: digital height model (model of the height of natural and built features from the ground)
# Overview

## Workflow

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
* Compute a DSM and a DTM with the same interpolation method
* Compute DHM as DSM - DTM

```
DSM - DTM -> DHM
```

## In this repo

This repo contains:
* code to compute the interpolation step on one tile
* code to compute the DHM from DSM and DTM on one tile
* scripts to compute the buffer step on one tile,
using the [ign-pdal-tools](http://gitlab.forge-idi.ign.fr/Lidar/pdalTools) library
* a script to run all steps together on a folder containing several tiles

## Interpolation

The testing environment so far includes implementations for:
* TIN-linear and Laplace interpolation via startin
* constrained Delaunay-based (CDT) TIN-linear and natural neighbour (NN) interpolation via CGAL
* radial IDW via GDAL/PDAL and quadrant-based IDW via scipy cKDTree and our own code.

During the interpolation step, a shapefile can be provided to mask polygons using a nodata value.

More information on IDW in [More about the IDW algorithms](#more-about-the-idw-algorithms).

## Output format

**TODO**

# Installation

Install the conda environment for this repo using [mamba](https://github.com/mamba-org/mamba) (faster
reimplementation of conda):

```bash
make install
conda activate produits_derives_lidar
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

> **Warning** In all steps, the tiles are supposed to be named following this syntax:
> `prefix1_prefix2_{coord_x}_{coord_y}_suffix` where
> `coord_x` and `coord_y` are the coordinates of the top-left corner of the tile.
> By default, they are given in km, and the tile width is 1km. Otherwise, you must override the
> values of `tile_geometry.tile_width` and `tile_geometry.tile_coord_scale`
> * `tile_geometry.tile_width` must contain the tile size in meters
> * `tile_geometry.tile_coord_scale` must contain the `coord_x` and `coord_y` scale so that `coord_{x or y} * tile_geometry.tile_coord_scale` are the coordinates of the top-left corner in meters

## Whole pipeline

To run the whole pipeline (DSM + DTM + DHM) on all the LAS files in a folder, using all the
available interpolation method, use `run.sh`.

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
  * ${OUTPUT_DIR}/ground : filtered las for DTM generation
  * ${OUTPUT_DIR}/ground_with_buffer : buffered las for DTM generation
  * ${OUTPUT_DIR}/upground : filtered las for DSM generation
  * ${OUTPUT_DIR}/upground_with_buffer : buffered las for DSM generation
* Output folders:
  * ${OUTPUT_DIR}/DTM
  * ${OUTPUT_DIR}/DSM
  * ${OUTPUT_DIR}/DHM


## Buffer

To add a buffer to a point cloud using `ign-pdal-tools`:

```bash
python -m produits_derives_lidar.filter_one_tile \
  io.input_dir=INPUT_DIR \
  io.input_filename=INPUT_FILENAME \
  io.output_dir=OUTPUT_DIR \
  buffer.size=10
```

Any other parameter in the `./configs` tree can be overriden in the command (see the doc of
[hydra](https://hydra.cc/) for more details on usage)

## Interpolation

To run interpolation (DXM generation) using a given method:

```bash
python -m produits_derives_lidar.ip_one_tile \
    io.input_dir=${BUFFERED_DIR} \
    io.input_filename={} \
    io.output_dir=${DXM_DIR} \
    interpolation=${METHOD} \
    tile_geometry.pixel_size=${PIXEL_SIZE}
    filter.keep_classes=[2,66]
```

`filter.keep_classes` must be a list inside `[]`, separated by `,` without spaces.

`interpolation` must be the stem of one of the filenames in `configs/interpolation`

Any other parameter in the `./configs` tree can be overriden in the command (see the doc of
[hydra](https://hydra.cc/) for more details on usage)

During the interpolation step, a shapefile can be provided to mask polygons using `tile_geometry.no_data_value`.
To use it, provide the shapefile path with the `io.no_data_mask_shapefile` argument.

## DHM

To generate DHM:
```bash
    python -m produits_derives_lidar.dhm_one_tile \
        dhm.input_dsm_dir=${DSM_DIR} \
        dhm.input_dtm_dir=${DTM_DIR} \
        io.input_filename={} \
        io.output_dir=${DHM_DIR} \
        interpolation=${METHOD} \
        tile_geometry.pixel_size=${PIXEL_SIZE}

```
`dhm.input_dsm_dir` and `dhm.input_dtm_dir` must contained DSM and DTM generated with
`produits_derives_lidar.ip_one_tile` using the same interpolation method an pixel_size as given in
arguments.

Any other parameter in the `./configs` tree can be overriden in the command (see the doc of
[hydra](https://hydra.cc/) for more details on usage)



# Docker

This codebase can be used in a docker image.

To generate the docker image, run `make docker-build`

To deploy it on nexus, run `make docker-deploy`

To run any of the methods cited in the [Usage section](#usage):
```bash
# Example for interpolation
docker run -t --rm --userns=host --shm-size=2gb \
    -v $INPUT_DIR:/input
    -v $OUTPUT_DIR:/output
    lidar_hd/produits_derives_lidar:$VERSION
    python -m produits_derives_lidar.ip_one_tile \
        io.input_dir=/input \
        io.input_filename=$FILENAME \
        io.output_dir=/output \
        interpolation=$METHOD \
        tile_geometry.pixel_size=$PIXEL_SIZE
```

The version number can be retrieved with `python -m produits_derives_lidar.version`


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
1. Create conda environment : `conda env create -n produits_derives_lidar -f environment.yml`
2. Activate conda environment : `conda activate produits_derives_lidar`
2. Launch the module : `python -m [name of the module to run] [argument_1] [argument_2] [...]`

Another word of caution with the outputs is that they all use a fixed no-data value of -9999. This includes the GeoTIFF exporter. To view the results correctly, you should keep in mind that while the upper bounds of the data will be determined correctly by the viewer software (e.g. QGIS), the lower bound will be -9999.

**Note:** ASC export is not currently supported for the PDAL-IDW algorithm.

**Another note:** You are advised to configure the IDWquad parametrisation **with performance in mind** when first getting started. Otherwise it might take _veeeeeery long_ to finish.

# More about the IDW algorithms

### PDAL-IDW
The PDAL-IDW workflow is actually built on top of GDAL, but since GDAL does not play well with Python data structures, I used the interface that is provided within PDAL's pipeline framework to implement it. No part of the program currently uses the Python bindings of GDAL directly, but we might need to eventually start working with it. The ellipsoidal IDW features cannot be accessed through PDAL's interface for GDAL, hence they cannot be used here (hence PDAL-IDW only accepts one radius). There is a neat extra feature in the PDAL interface though, it allows a fallback method to be used. If you specify a value for an interpolation window (IDW argument 3 above), wherever radial IDW fails, the program will look for values within a square kernel of pixels around the pixel that is being interpolated (presumably after the first round of true IDW interpolation). For example, if you provide a value of 10 for this argument, it will look for values in a 10x10 square kernel around the pixel for values, weighting them based on their distance from the pixel that is being interpolated. This can theoretically make the result more or less continuous (a bit more like the Voronoi and TIN-based methods).

### IDWquad
This is a quadrant-based IDW implementation that is not built on top of third-party software (apart from scipy, from which cKDTree is used). It builds a KD-tree representation of the points of the input tile and overlays it with a raster of the desired dimensions. For each pixel, it iteratively queries more and more points until it has enough points **per quadrant** to consider an IDW interpolation reliable. The algorithm can either base its KD-tree queries on k-nearest neighbours to find, or a query radius to search within.
I'll explain how it works by giving some more detail about the parameters, listing them in the same order as in the list of arguments above.

* **Starting interpolation radius/number of neighbours _k_ to query:** The starting value for the radius or number of neighbours to query. This is the value that will be incremented until enough points per quadrant can be found to interpolate a value for the pixel.
* **Interpolation power:** this is self-explanatory, it is the power that is used _if_ IDW interpolation can take place based on the number of neighbours per quadrant that were found.
* **Minimum number of points to find per quadrant:** the minimum number of neighbours to find in _each_ quadrant to interpolate a value for the pixel. E.g. if it is set to one, the algorithm will be satisfied by finding only one neighbour per quadrant. If you set it to a higher value, it will increase the radius/number of neighbours to find until it finds that many neighbours per quadrant (or reaches the maximum number of iterations).
* **Increment value:** the algorithm will increase the radius/number of closest neighbours queried by this amount in each iteration until there are enough neighbours per quadrant to interpolate.
* **Method:** as already explained, you can either specify "radial" to make the algorithm iteratively expand its search radius, or "k-nearest" to iteratively increase the number of nearest neighbours to query.
* **Tolerance value _eps_:** this is very important in terms of performance. As we discussed with Ravi on Discord, the best way to increase performance here is to use _approximate_ KD-tree queries rather than exact queries. Fine tune this parameter to drastically improve performance. This does not affect continuity, it does however affect quality. You can find more info about this on the following pages:
	* If you use radial queries: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.query_ball_point.html#scipy.spatial.cKDTree.query_ball_point
	* If you use k-nearest queries: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.query.html#scipy.spatial.cKDTree.query
* **Iteration limit:** you may further fine-tune performance by setting a limit on how many times the algorithm may increment the radius/number of neighbours to find. In some cases this may also drastically improve performance at the cost of continuity.
