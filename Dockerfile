FROM amd64/ubuntu:latest

WORKDIR /app

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3 python3-setuptools pip git \
        libxml2-utils libprotobuf-dev protobuf-compiler \
        gdal-bin libgdal-dev python3-gdal && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/roelderickx/ogr2osm.git && \
    cd ogr2osm && \
    python3 setup.py install

RUN pip install --break-system-packages lxml packaging

ENTRYPOINT ["ogr2osm"]
