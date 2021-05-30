FROM amd64/ubuntu:20.04

WORKDIR /app

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libxml2-utils \
    gdal-bin \
    libgdal-dev \
    python-is-python3 \
    python3-gdal \
    libprotobuf-dev \
    protobuf-compiler \
    osmctools \
    pip

RUN unlink /etc/localtime
RUN ln -s /usr/share/zoneinfo/Europe/Brussels /etc/localtime

RUN pip install cram lxml
RUN pip install --upgrade protobuf

