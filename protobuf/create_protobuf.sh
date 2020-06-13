#!/bin/bash

rm fileformat.proto ../ogr2pbf/fileformat_pb2.py
echo 'syntax = "proto2";' > fileformat.proto
curl -L https://github.com/openstreetmap/OSM-binary/raw/master/src/fileformat.proto >> fileformat.proto
protoc --python_out=../ogr2pbf ./fileformat.proto

rm osmformat.proto ../ogr2pbf/osmformat_pb2.py
echo 'syntax = "proto2";' > osmformat.proto
curl -L https://github.com/openstreetmap/OSM-binary/raw/master/src/osmformat.proto >> osmformat.proto
protoc --python_out=../ogr2pbf ./osmformat.proto

