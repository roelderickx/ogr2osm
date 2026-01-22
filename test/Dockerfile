FROM amd64/ubuntu:latest

WORKDIR /app

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        libxml2-utils \
        python-is-python3 \
        pip && \
    unlink /etc/localtime && \
    ln -s /usr/share/zoneinfo/Europe/Brussels /etc/localtime

RUN apt-get install -y \
        gdal-bin \
        libgdal-dev \
        python3-gdal \
        libprotobuf-dev \
        protobuf-compiler \
        osmctools

RUN pip install --break-system-packages cram lxml packaging
RUN pip install --break-system-packages --upgrade protobuf

ENTRYPOINT ["cram"]
