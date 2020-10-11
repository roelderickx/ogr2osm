# ogr2pbf
A tool for converting ogr-readable files like shapefiles into .pbf or .osm data

## Installation

Ogr2pbf requires python 3, gdal with python bindings, lxml and protobuf. Depending on the file formats you want to read you may have to compile gdal yourself but there should be no issues with shapefiles.

### Using pip
```bash
pip install --upgrade ogr2pbf
```

### From source
Clone this repository and run the following command in the created directory.
```bash
python setup.py install
```

## About

This program is based on [pnorman's version of ogr2osm](https://github.com/pnorman/ogr2osm), but is rewritten to make it useable as a general purpose library.

Ogr2pbf will read any data source that ogr can read and handle reprojection for you. It takes a python file to translate external data source tags into OSM tags, allowing you to use complicated logic. If no translation is specified it will use an identity translation, carrying all tags from the source to the .pbf or .osm output.

## Import Cautions

Anyone planning an import into OpenStreetMap should read and review the import guidelines located [on the wiki](http://wiki.openstreetmap.org/wiki/Import/Guidelines). When writing your translation file you should look at other examples and carefully consider each external data source tag to see if it should be converted to an OSM tag.

## Usage

Ogr2pbf can be used as a standalone application, but you can also use its classes in your own python project.

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
  --gis-order           Consider the source coordinates to be in traditional
                        GIS order
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

Example code:
```python
import ogr2pbf

# 1. Required parameters for this example:

# - datasource_parameter is a variable holding the input filename, or a
#   database connection such as "PG:dbname=pdx_bldgs user=emma host=localhost"
datasource_parameter = ...

# - in case your datasource is a database, you will need a query
query = ...

# - the output file to write
output_file = ...

# 2. Create the translation object. If no translation is required you
#    can use the base class from ogr2pbf, otherwise you need to instantiate
#    a subclass of ogr2pbf.TranslationBase
translation_object = ogr2pbf.TranslationBase()

# 3. Create the ogr datasource. You can specify a source projection but
#    EPSG:4326 will be assumed if none is given and if the projection of the
#    datasource is unknown.
datasource = ogr2pbf.OgrDatasource(translation_object)
datasource.open_datasource(datasource_parameter)

# 4. If the datasource is a database then you must set the query to use.
#    Setting the query for any other datasource is useless but not an error.
datasource.set_query(query)

# 5. Instantiate the ogr to osm converter class ogr2pbf.OsmData and start the
#    conversion process
osmdata = ogr2pbf.OsmData(translation_object)
osmdata.process(datasource)

# 6. Instantiate either ogr2pbf.OsmDataWriter or ogr2pbf.PbfDataWriter and
#    invoke output() to write the output file. If required you can write a
#    custom datawriter class by subclassing ogr2pbf.DataWriterBase.
datawriter = ogr2pbf.OsmDataWriter(output_file)
osmdata.output(datawriter)
```

Refer to [contour-osm](https://github.com/roelderickx/contour-osm) for a complete example with a custom translation class and coordinate reprojection.

## Translations

Just like ogr2osm, ogr2pbf supports custom translations for your data. To do this you need to subclass ogr2pbf.TranslationBase and override the methods in which you want to run custom code.

```python
class TranslationBase:
    # Override this method if you want to modify the given layer,
    # or return None if you want to suppress the layer
    def filter_layer(self, layer):
        return layer
    
    # Override this method if you want to modify the given feature,
    # or return None if you want to suppress the feature
    # note 1: fieldNames parameter has been removed from the original ogr2osm,
    # but can be recovered from the ogrfeature parameter:
    # ---
    # feature_def = ogrfeature.GetDefnRef()
    # field_names = []
    # for i in range(feature_def.GetFieldCount()):
    #     field_names.append(feature_def.GetFieldDefn(i).GetNameRef())
    # ---
    # note 2: reproject is a function to convert the feature to 4326 projection
    # with coordinates in traditional gis order. However, do not return the
    # reprojected feature since it will be done again in ogr2pbf.
    def filter_feature(self, ogrfeature, reproject):
        return ogrfeature
    
    # Override this method if you want to modify or add tags to the xml output
    def filter_tags(self, tags):
        return tags
    
    # This method is called after the creation of an OsmGeometry object. The
    # ogr feature and ogr geometry used to create the object are passed as
    # well. Note that any return values will be discarded by ogr2pbf.
    def process_feature_post(self, osmgeometry, ogrfeature, ogrgeometry):
        pass
    
    # Override this method if you want to modify the list of nodes, ways or
    # relations, or take any additional actions right before writing the
    # objects to the OSM file. Note that any return values will be discarded
    # by ogr2pbf.
    def process_output(self, osmnodes, osmways, osmrelations):
        pass
```

