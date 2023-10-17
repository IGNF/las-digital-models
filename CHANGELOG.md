# dev
- refactor steps to create fewer intermediate results

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
