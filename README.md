# Filter LIDAR (keep only ground) + Interpolation

**This is the Python repo of the filter LIDAR, then ground interpolation**

## In repo:

* `README.md` _(this readme file)_
* `filter_one_tile.py` _(main file for filtering LIDAR by classes: eg. keep only ground for a single tile)_
* `filter_multiprocessing.py` _(main file for filtering LIDAR by classes: eg. keep only ground for a whole folder using multiprocessing to run faster)_
* `ip_one_tile.py` _(main file for interpolation on a single tile)_
* `ip_multiprocessing.py` _(main file for interpolation on a whole folder using multiprocessing to run faster)_
* folder `docker` _(contains tools to run each step in a docker container)_
* folder `tasks` _(severals tasks)_
* folder `commons` _(common tools)_

The testing environment so far includes multiprocessing pool-based implementations TIN-linear and Laplace interpolation via startin, constrained Delaunay-based (CDT) TIN-linear and natural neighbour (NN) interpolation via CGAL, radial IDW via GDAL/PDAL and quadrant-based IDW via scipy cKDTree and our own code.

## How to run

The code in this repo can be executed either after being installed on your computer or via a docker image.

### Run With docker
_Tested on Linux only for the moment_
Build docker image by running:

```bash
bash docker/build.sh
```

- Run preprocessing on one tile by editing and running `docker/run_filter.sh`
- Run interpolation on one tile by editing and running `docker/run_ip.sh`

To run on a whole folder, use gpao to manage the process with http://gitlab.forge-idi.ign.fr/Lidar/ProduitDeriveLidarGpao (work in progress as of january 2023)


### Run with direct installation
Install the conda environment for this repo:
```bash
bash setup_env/setup_env.sh
```
You can run ground filtering and interpolation on a single tile with:
* `python -m produit_derive_lidar.filter_one_tile [YOUR ARGUMENTS]`
* `python -m produit_derive_lidar.ip_one_tile [YOUR ARGUMENTS]`
(cf. `python -m produit_derive_lidar.filter_one_tile` for the arguments list)

You can run on a whole folder, using multiprocessing by following the instructions below

### Run with multiprocessing

You can find examples in `example_run_dsm.sh` and `example_run_dtm.sh`
#### Primary (filter pointcloud by classes)
You are advised to run `filter_multiprocessing` **from the console**, preferably from Anaconda Prompt. If you run it from an IDE, it will probably not fork the processes properly.

Run `python -m produit_derive_lidar.filter_multiprocessing -h` to get the whole signature of the script

Here is an example:
```bash
python -m produit_derive_lidar.filter_multiprocessing -i ${origin_dir} -o ${filtered_las_dir} --keep_classes 2 66
optional arguments:
  -h, --help            show this help message and exit
  --input_dir INPUT_DIR, -i INPUT_DIR
                        Input file on which to run the pipeline (most likely located in PDAL folder 'data'). The script assumes that the neighbor tiles are located in the same folder
                        as the queried tile
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        Directory folder for saving the filtered tiles
  --extension {las,laz}, -e {las,laz}
                        extension
  --spatial_reference SPATIAL_REFERENCE
                        Spatial reference to use to override the one from input las.
  --keep_classes KEEP_CLASSES [KEEP_CLASSES ...]
                        Classes to keep when filtering. Default: ground + virtual points. To provide a list, follow this example : '--keep_classes 2 66 291'
  --cpu_limit CPU_LIMIT
                        Maximum number of cpus to use (Default: use cpu_count - 1)
```

#### Secondary entry point (interpolation + post-processing)

You are advised to run `ip_multiprocessing` **from the console**, preferably from Anaconda Prompt. If you run it from an IDE, it will probably not fork the processes properly.

Run `python -m produit_derive_lidar.ip_multiprocessing  -h` to get the whole signature of the script

Here is an example:
```bash
python -m produit_derive_lidar.ip_multiprocessing -i ${origin_dir} -f ${filtered_las_dir} -o ${output_dir}

optional arguments:
  -h, --help            show this help message and exit
  --origin_dir ORIGIN_DIR, -i ORIGIN_DIR
                        Folder containing the origin lidar tiles (before filtering).Used to retrieve the tile bounding box.
  --filtered_las_dir FILTERED_LAS_DIR, -f FILTERED_LAS_DIR
                        Folder containing the input filtered tiles.
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        Directory folder for saving the outputs.
  --temp_dir TEMP_DIR, -t TEMP_DIR
                        Directory folder for saving intermediate results
  --extension {las,laz}, -e {las,laz}
                        extension
  --postprocessing {0,1,2,3,4}, -p {0,1,2,3,4}
                        post-processing mode, currently these ones are available: - 0 (default, does not run post-processing) - 1 (runs missing pixel value patching only) - 2 (runs
                        basic flattening only) - 3 (runs both patching and basic flattening) - 4 (runs patching, basic flattening and hydro-flattening)
  --pixel_size PIXEL_SIZE, -s PIXEL_SIZE
                        pixel size (in metres) for interpolation
  --interpolation_method {startin-TINlinear,startin-Laplace,CGAL-NN,PDAL-IDW,IDWquad}, -m {startin-TINlinear,startin-Laplace,CGAL-NN,PDAL-IDW,IDWquad}
                        interpolation method)
  --spatial_reference SPATIAL_REFERENCE
                        Spatial reference to use to override the one from input las.
  --buffer_width BUFFER_WIDTH
                        Width (in meter) for the buffer that is added to the tile before interpolation (to prevent artefacts)
  --cpu_limit CPU_LIMIT
                        Maximum number of cpus to use (Default: use cpu_count - 1)

All IDW parameters are optional, but it is assumed the user will fine-tune them, hence the defaults are not listed. Output files will be written to the target folder, tagged with
thename of the interpolation method that was used.

```

## A word of caution

If you are using an Anaconda virtual environment for PDAL/CGAL, you should first activate the environment in Anaconda prompt and _then_ run the relevant script
from the same prompt. So, for example:
1. Create conda environment : `conda env create -n produit_derive_lidar -f environment.yml`
2. Activate conda environment : `conda activate produit_derive_lidar`
2. Launch the module : `python -m [name of the module to run] [argument_1] [argument_2] [...]`

Another word of caution with the outputs is that they all use a fixed no-data value of -9999. This includes the GeoTIFF exporter. To view the results correctly, you should keep in mind that while the upper bounds of the data will be determined correctly by the viewer software (e.g. QGIS), the lower bound will be -9999.

**Note:** ASC export is not currently supported for the PDAL-IDW algorithm.

**Another note:** You are advised to configure the IDWquad parametrisation **with performance in mind** when first getting started. Otherwise it might take _veeeeeery long_ to finish.

## More about the IDW algorithms

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
