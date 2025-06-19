FROM mambaorg/micromamba:latest AS mamba_pdal
COPY environment.yml /environment.yml
USER root
RUN micromamba env create -n las_digital_models -f /environment.yml


FROM debian:bullseye-slim

# install PDAL
COPY --from=mamba_pdal /opt/conda/envs/las_digital_models/bin/pdal /opt/conda/envs/las_digital_models/bin/pdal
# install gdal
COPY --from=mamba_pdal /opt/conda/envs/las_digital_models/bin/*gdal* /opt/conda/envs/las_digital_models/bin/
COPY --from=mamba_pdal /opt/conda/envs/las_digital_models/bin/python /opt/conda/envs/las_digital_models/bin/python
COPY --from=mamba_pdal /opt/conda/envs/las_digital_models/lib/ /opt/conda/envs/las_digital_models/lib/
COPY --from=mamba_pdal /opt/conda/envs/las_digital_models/ssl /opt/conda/envs/las_digital_models/ssl
COPY --from=mamba_pdal /opt/conda/envs/las_digital_models/share/proj/proj.db /opt/conda/envs/las_digital_models/share/proj/proj.db

ENV PATH=$PATH:/opt/conda/envs/las_digital_models/bin/
ENV PROJ_LIB=/opt/conda/envs/las_digital_models/share/proj/

WORKDIR /ProduitDeriveLIDAR
RUN mkdir tmp
COPY las_digital_models las_digital_models
COPY test test
COPY configs configs