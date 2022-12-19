FROM continuumio/miniconda3

# set the IGN proxy, otherwise apt-get and other applications don't work
# Should be commented out outside of IGN
ENV http_proxy 'http://192.168.4.9:3128/'
ENV https_proxy 'http://192.168.4.9:3128/'

# Remove any third-party apt sources to avoid issues with expiring keys.
RUN rm -f /etc/apt/sources.list.d/*.list

# Install some basic utilities
RUN apt-get update && apt-get install -y \
        curl \
        ca-certificates \
        sudo \
        git \
        bzip2 \
        libx11-6 \
        postgis \
        && rm -rf /var/lib/apt/lists/*

# Create a working directory
RUN mkdir /app

# Set up the Conda environment
COPY setup_env/environment.yml /app/environment.yml
RUN conda env update -n base -f /app/environment.yml \
        && rm -r /app/environment.yml \
        && conda clean -ya

# Copy the repository content in /app
WORKDIR /app
COPY . .

# Set the default command to bash for image inspection.
CMD ["bash"]

