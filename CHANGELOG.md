# v2.1.0
Custom PDAL: in the docker image, compile custom PDAL (waiting for PDAL 2.9)
fix run_extract_z_virtual_lines_from_raster: ouput geometries are only LineString (no more MultiLineString) 

# v2.0.0
Rename produit_derive_lidar to las_digital_models

# v1.2.1
Fix path to hydra config in Z values extraction

# v1.2.0
[New feature] run the extraction of minimum Z values along lines (defined in a geometry file) from raster containing Z value

# v1.1.0
- **API CHANGE**: update filter API: use `dimension` + `keep_values` instead of `keep_classes` to be more flexible in
the prefiltering step
- remove unused interpolation methods

# v1.0.2
- add gdal executables to docker image (to generate cog)

# v1.0.1
- fix jenkinsfile (deployment part)
- mark tests to skip inside docker image
- update ign-pdal-tools to 1.5.1 (fix misclassification due to las rewriting with wrong format)

# v1.0.0
- refactor docker image tools (reduce docker image size)
- refactor python version (standardize with other tools)
- remove hydra internal logs
- fix jenkinsfile (continuous integration)
- add (+ apply) linting and pre-commit
- remove dead code
- [BREAKING CHANGE] uniformise produit(s)_derive(s)_lidar to produits_derives_lidar
- use gdal_calc from osgeo instead of lidarutils
- remove gdal warning (explicitly set gdal.UseExceptions())
- update readme

# v0.4.0
- refactor steps to create fewer intermediate results
- bump to pdal 2.6.0 (should resolve [#2277](http://redmine.forge-idi.ign.fr/issues/2277))

# v0.3.0:
- only use hydra on main function of ip_one_tile / add_buffer_one_tile / filter_one_tile
- add possibility to overwrite no-data in polygons from a shapefile after interpolation (eg. for ZICAD)
- use Mamba for python environment generation in docker

# v0.2.3:
- Continuous Integration with Jenkins
- Use "standard" grid for TIF output. This implies using the las tiles filenames to get the
expected extent of the las data, and modifying the interpolation parameters to use that grid
- Use hydra to handle parameters
- replace python parallelisation by the use of gnu-parallel (cf. run.sh)

# v0.2.2:
Fix no-data value when saving with rasterio (no value was set) or gdalcalc (same)

# v0.2.1:
intermediate results are no more forced to be in las format (can be laz)

# v0.2.0:
run DSM/DTM/DHM
