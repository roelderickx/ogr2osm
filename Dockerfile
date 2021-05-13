FROM osgeo/gdal:ubuntu-full-3.2.2

WORKDIR /app

RUN apt-get update \
  && apt-get install -y \
    libprotobuf-dev \
    libxml2-utils \
    osmctools \
    protobuf-compiler \
    python3-pip

RUN pip3 install \
  --no-cache-dir \
  cram \
  lxml \
  protobuf

# A clumsy hack to avoid errors
RUN cd /usr/lib/python3/dist-packages/osgeo \
  && ln -s ./_gdal.cpython*.so ./_gdal.so \
  && ln -s ./_gdal_array.cpython*.so ./_gdal_array.so \
  && ln -s ./_gdalconst.cpython*.so ./_gdalconst.so \
  && ln -s ./_gnm.cpython*.so ./_gnm.so \
  && ln -s ./_ogr.cpython*.so ./_ogr.so \
  && ln -s ./_osr.cpython*.so ./_osr.so

ENV PYTHONPATH=/usr/lib/python3/dist-packages/

COPY ./ ./

ENTRYPOINT ["python3", "-m", "ogr2osm"]
