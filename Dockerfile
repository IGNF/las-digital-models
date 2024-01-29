FROM mambaorg/micromamba:latest as mamba_pdal
COPY environment.yml /environment.yml
USER root
RUN micromamba env create -n produits_derives_lidar -f /environment.yml


FROM debian:bullseye-slim

# install PDAL
COPY --from=mamba_pdal /opt/conda/envs/produits_derives_lidar/bin/pdal /opt/conda/envs/produits_derives_lidar/bin/pdal
# install gdal
COPY --from=mamba_pdal /opt/conda/envs/produits_derives_lidar/bin/*gdal* /opt/conda/envs/produits_derives_lidar/bin/
COPY --from=mamba_pdal /opt/conda/envs/produits_derives_lidar/bin/python /opt/conda/envs/produits_derives_lidar/bin/python
COPY --from=mamba_pdal /opt/conda/envs/produits_derives_lidar/lib/ /opt/conda/envs/produits_derives_lidar/lib/
COPY --from=mamba_pdal /opt/conda/envs/produits_derives_lidar/ssl /opt/conda/envs/produits_derives_lidar/ssl
COPY --from=mamba_pdal /opt/conda/envs/produits_derives_lidar/share/proj/proj.db /opt/conda/envs/produits_derives_lidar/share/proj/proj.db

ENV PATH=$PATH:/opt/conda/envs/produits_derives_lidar/bin/
ENV PROJ_LIB=/opt/conda/envs/produits_derives_lidar/share/proj/

WORKDIR /ProduitDeriveLIDAR
RUN mkdir tmp
COPY produits_derives_lidar produits_derives_lidar
COPY test test
COPY configs configs