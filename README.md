# ogr2pbf
A tool for converting ogr-readable files like shapefiles into .pbf or .osm data

## Installation

Ogr2pbf requires python 3, gdal with python bindings, lxml and protobuf. Depending on the file formats you want to read you may have to compile gdal yourself but there should be no issues with shapefiles.

## About

This program is based on [pnorman's version of ogr2osm](https://github.com/pnorman/ogr2osm), but is rewritten to make it useable as a general purpose library.

Ogr2pbf will read any data source that ogr can read and handle reprojection for you. It takes a python file to translate external data source tags into OSM tags, allowing you to use complicated logic. If no translation is specified it will use an identity translation, carrying all tags from the source to the .pbf or .osm output.

## Import Cautions

Anyone planning an import into OpenStreetMap should read and review the import guidelines located [on the wiki](http://wiki.openstreetmap.org/wiki/Import/Guidelines). When writing your translation file you should look at other examples and carefully consider each external data source tag to see if it should be converted to an OSM tag.

## Usage

Ogr2pbf can be used as a standalone application, but you can use its classes in your own python project.

### Standalone

```
usage: ogr2pbf [-h] [-t TRANSLATION] [--encoding ENCODING] [--sql SQLQUERY]
               [--no-memory-copy] [-e EPSG_CODE] [-p PROJ4_STRING]
               [--significant-digits SIGNIFICANTDIGITS]
               [--rounding-digits ROUNDINGDIGITS]
               [--split-ways MAXNODESPERWAY] [--id ID] [--idfile IDFILE]
               [--saveid SAVEID] [-o OUTPUT] [-f] [--no-upload-false]
               [--never-download] [--never-upload] [--locked]
               DATASOURCE

positional arguments:
  DATASOURCE            DATASOURCE can be a file path or a org PostgreSQL
                        connection string such as: "PG:dbname=pdx_bldgs
                        user=emma host=localhost" (including the quotes)

optional arguments:
  -h, --help            show this help message and exit
  -t TRANSLATION, --translation TRANSLATION
                        Select the attribute-tags translation method. See the
                        translations/ directory for valid values.
  --encoding ENCODING   Encoding of the source file. If specified, overrides
                        the default of utf-8
  --sql SQLQUERY        SQL query to execute on a PostgreSQL source
  --no-memory-copy      Do not make an in-memory working copy
  -e EPSG_CODE, --epsg EPSG_CODE
                        EPSG code of source file. Do not include the 'EPSG:'
                        prefix. If specified, overrides projection from source
                        metadata if it exists.
  -p PROJ4_STRING, --proj4 PROJ4_STRING
                        PROJ.4 string. If specified, overrides projection from
                        source metadata if it exists.
  --significant-digits SIGNIFICANTDIGITS
                        Number of decimal places for coordinates to output
                        (default: 9)
  --rounding-digits ROUNDINGDIGITS
                        Number of decimal places for rounding when snapping
                        nodes together (default: 7)
  --split-ways MAXNODESPERWAY
                        Split ways with more than the specified number of
                        nodes. Defaults to 1800. Any value below 2 - do not
                        split.
  --id ID               ID to start counting from for the output file.
                        Defaults to 0.
  --idfile IDFILE       Read ID to start counting from from a file.
  --saveid SAVEID       Save last ID after execution to a file.
  -o OUTPUT, --output OUTPUT
                        Set destination .osm file name and location.
  -f, --force           Force overwrite of output file.
  --no-upload-false     Omit upload=false from the completed file to surpress
                        JOSM warnings when uploading.
  --never-download      Prevent JOSM from downloading more data to this file.
  --never-upload        Completely disables all upload commands for this file
                        in JOSM, rather than merely showing a warning before
                        uploading.
  --locked              Prevent any changes to this file in JOSM, such as
                        editing or downloading, and also prevents uploads.
                        Implies upload="never" and download="never".
```

### As a library

Currently the API is still under development and may be subject to changes without prior warning.

## Translations

Just like ogr2osm, ogr2pbf supports custom translations for your data. Documentation will follow here as soon as the API is complete.

## TODO

This application is still in beta stage. It needs profound testing of the PBF output, as well as some tweaks to limit the amount of nodes or ways in one block. The API has to be completed, especially with regard to the datawriter.
The datawriter should be automatically chosen based on the file extension, or if no output parameter is present it should automatically be pbf.

