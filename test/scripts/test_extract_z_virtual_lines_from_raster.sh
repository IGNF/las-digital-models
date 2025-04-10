python -u -m produits_derives_lidar.extract_stat_from_raster.extract_z_virtual_lines_from_raster \
    --input_las test/data/bridge/pointcloud/test_semis_2023_0299_6802_LA93_IGN69.laz \
    --input_raster test/data/bridge/mns_hydro_postfiltre/test_mns_hydro_2023_0299_6802_LA93_IGN69.tif \
    --input_geometry test/data/bridge/input_operators/NUALHD_1-0_DF_lignes_contrainte.shp\
    --output_geometry test/data/bridge/output/test_lines_2023_0299_6802_LA93_IGN69.geojson \
    --spatial_ref "EPSG:2154" \
    --tile_width 1000 