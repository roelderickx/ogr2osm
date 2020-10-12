  $ [ "$0" != "/bin/bash" ] || shopt -s expand_aliases
  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ alias ogr2pbf="PYTHONPATH=$TESTDIR/.. $PYTHON -m ogr2pbf"

usage:
  $ ogr2pbf -h
  usage: __main__.py [-h] [-t TRANSLATION] [--encoding ENCODING]
                     [--sql SQLQUERY] [--no-memory-copy] [-e EPSG_CODE]
                     [-p PROJ4_STRING] [--gis-order]
                     [--significant-digits SIGNIFICANTDIGITS]
                     [--rounding-digits ROUNDINGDIGITS]
                     [--split-ways MAXNODESPERWAY] [--id ID] [--idfile IDFILE]
                     [--saveid SAVEID] [-o OUTPUT] [-f] [--osm]
                     [--no-upload-false] [--never-download] [--never-upload]
                     [--locked]
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
    --osm                 Write the output as an OSM file in stead of a PBF file
    --no-upload-false     Omit upload=false from the completed file to suppress
                          JOSM warnings when uploading.
    --never-download      Prevent JOSM from downloading more data to this file.
    --never-upload        Completely disables all upload commands for this file
                          in JOSM, rather than merely showing a warning before
                          uploading.
    --locked              Prevent any changes to this file in JOSM, such as
                          editing or downloading, and also prevents uploads.
                          Implies upload="never" and download="never".
						  
require_output_file_when_using_db_source:
  $ ogr2pbf "PG:dbname=test"
  usage: __main__.py [-h] [-t TRANSLATION] [--encoding ENCODING]
                     [--sql SQLQUERY] [--no-memory-copy] [-e EPSG_CODE]
                     [-p PROJ4_STRING] [--gis-order]
                     [--significant-digits SIGNIFICANTDIGITS]
                     [--rounding-digits ROUNDINGDIGITS]
                     [--split-ways MAXNODESPERWAY] [--id ID] [--idfile IDFILE]
                     [--saveid SAVEID] [-o OUTPUT] [-f] [--osm]
                     [--no-upload-false] [--never-download] [--never-upload]
                     [--locked]
                     DATASOURCE
  __main__.py: error: ERROR: An output file must be explicitly specified when using a database source
  [2]

require_query_when_using_db_source:
  $ ogr2pbf "PG:dbname=test" -o test.osm
  usage: __main__.py [-h] [-t TRANSLATION] [--encoding ENCODING]
                     [--sql SQLQUERY] [--no-memory-copy] [-e EPSG_CODE]
                     [-p PROJ4_STRING] [--gis-order]
                     [--significant-digits SIGNIFICANTDIGITS]
                     [--rounding-digits ROUNDINGDIGITS]
                     [--split-ways MAXNODESPERWAY] [--id ID] [--idfile IDFILE]
                     [--saveid SAVEID] [-o OUTPUT] [-f] [--osm]
                     [--no-upload-false] [--never-download] [--never-upload]
                     [--locked]
                     DATASOURCE
  __main__.py: error: ERROR: You must specify a query with --sql when using a database source
  [2]

require_db_source_for_sql_query:
  $ rm -f test1.osm
  $ ogr2pbf --osm $TESTDIR/shapefiles/test1.shp --sql="SELECT * FROM wombats"
  WARNING: You specified a query with --sql but you are not using a database source
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  PROJCS["NAD83 / UTM zone 10N",
      GEOGCS["NAD83",
          DATUM["North_American_Datum_1983",
              SPHEROID["GRS 1980",6378137,298.257222101,
                  AUTHORITY["EPSG","7019"]],
              AUTHORITY["EPSG","6269"]],
          PRIMEM["Greenwich",0,
              AUTHORITY["EPSG","8901"]],
          UNIT["degree",0.0174532925199433,
              AUTHORITY["EPSG","9122"]],
          AUTHORITY["EPSG","4269"]],
      PROJECTION["Transverse_Mercator"],
      PARAMETER["latitude_of_origin",0],
      PARAMETER["central_meridian",-123],
      PARAMETER["scale_factor",0.9996],
      PARAMETER["false_easting",500000],
      PARAMETER["false_northing",0],
      UNIT["metre",1,
          AUTHORITY["EPSG","9001"]],
      AXIS["Easting",EAST],
      AXIS["Northing",NORTH],
      AUTHORITY["EPSG","26910"]]
  Merging duplicate points in ways
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format test1.osm | diff -uNr - $TESTDIR/test1.xml

duplicatefile:
  $ ogr2pbf --osm $TESTDIR/shapefiles/test1.shp
  usage: __main__.py [-h] [-t TRANSLATION] [--encoding ENCODING]
                     [--sql SQLQUERY] [--no-memory-copy] [-e EPSG_CODE]
                     [-p PROJ4_STRING] [--gis-order]
                     [--significant-digits SIGNIFICANTDIGITS]
                     [--rounding-digits ROUNDINGDIGITS]
                     [--split-ways MAXNODESPERWAY] [--id ID] [--idfile IDFILE]
                     [--saveid SAVEID] [-o OUTPUT] [-f] [--osm]
                     [--no-upload-false] [--never-download] [--never-upload]
                     [--locked]
                     DATASOURCE
  __main__.py: error: ERROR: output file '.*test1.osm' exists (re)
  [2]

force:
  $ ogr2pbf --osm -f $TESTDIR/shapefiles/test1.shp
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  PROJCS["NAD83 / UTM zone 10N",
      GEOGCS["NAD83",
          DATUM["North_American_Datum_1983",
              SPHEROID["GRS 1980",6378137,298.257222101,
                  AUTHORITY["EPSG","7019"]],
              AUTHORITY["EPSG","6269"]],
          PRIMEM["Greenwich",0,
              AUTHORITY["EPSG","8901"]],
          UNIT["degree",0.0174532925199433,
              AUTHORITY["EPSG","9122"]],
          AUTHORITY["EPSG","4269"]],
      PROJECTION["Transverse_Mercator"],
      PARAMETER["latitude_of_origin",0],
      PARAMETER["central_meridian",-123],
      PARAMETER["scale_factor",0.9996],
      PARAMETER["false_easting",500000],
      PARAMETER["false_northing",0],
      UNIT["metre",1,
          AUTHORITY["EPSG","9001"]],
      AXIS["Easting",EAST],
      AXIS["Northing",NORTH],
      AUTHORITY["EPSG","26910"]]
  Merging duplicate points in ways
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format test1.osm | diff -uNr - $TESTDIR/test1.xml

nomemorycopy:
  $ ogr2pbf --osm -f --no-memory-copy $TESTDIR/shapefiles/test1.shp
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  PROJCS["NAD83 / UTM zone 10N",
      GEOGCS["NAD83",
          DATUM["North_American_Datum_1983",
              SPHEROID["GRS 1980",6378137,298.257222101,
                  AUTHORITY["EPSG","7019"]],
              AUTHORITY["EPSG","6269"]],
          PRIMEM["Greenwich",0,
              AUTHORITY["EPSG","8901"]],
          UNIT["degree",0.0174532925199433,
              AUTHORITY["EPSG","9122"]],
          AUTHORITY["EPSG","4269"]],
      PROJECTION["Transverse_Mercator"],
      PARAMETER["latitude_of_origin",0],
      PARAMETER["central_meridian",-123],
      PARAMETER["scale_factor",0.9996],
      PARAMETER["false_easting",500000],
      PARAMETER["false_northing",0],
      UNIT["metre",1,
          AUTHORITY["EPSG","9001"]],
      AXIS["Easting",EAST],
      AXIS["Northing",NORTH],
      AUTHORITY["EPSG","26910"]]
  Merging duplicate points in ways
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format test1.osm | diff -uNr - $TESTDIR/test1.xml

positiveid:
  $ ogr2pbf --osm -f --positive-id $TESTDIR/shapefiles/test1.shp
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  PROJCS["NAD83 / UTM zone 10N",
      GEOGCS["NAD83",
          DATUM["North_American_Datum_1983",
              SPHEROID["GRS 1980",6378137,298.257222101,
                  AUTHORITY["EPSG","7019"]],
              AUTHORITY["EPSG","6269"]],
          PRIMEM["Greenwich",0,
              AUTHORITY["EPSG","8901"]],
          UNIT["degree",0.0174532925199433,
              AUTHORITY["EPSG","9122"]],
          AUTHORITY["EPSG","4269"]],
      PROJECTION["Transverse_Mercator"],
      PARAMETER["latitude_of_origin",0],
      PARAMETER["central_meridian",-123],
      PARAMETER["scale_factor",0.9996],
      PARAMETER["false_easting",500000],
      PARAMETER["false_northing",0],
      UNIT["metre",1,
          AUTHORITY["EPSG","9001"]],
      AXIS["Easting",EAST],
      AXIS["Northing",NORTH],
      AUTHORITY["EPSG","26910"]]
  Merging duplicate points in ways
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format test1.osm | diff -uNr - $TESTDIR/positiveid.xml

version:
  $ ogr2pbf --osm -f --add-version $TESTDIR/shapefiles/test1.shp
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  PROJCS["NAD83 / UTM zone 10N",
      GEOGCS["NAD83",
          DATUM["North_American_Datum_1983",
              SPHEROID["GRS 1980",6378137,298.257222101,
                  AUTHORITY["EPSG","7019"]],
              AUTHORITY["EPSG","6269"]],
          PRIMEM["Greenwich",0,
              AUTHORITY["EPSG","8901"]],
          UNIT["degree",0.0174532925199433,
              AUTHORITY["EPSG","9122"]],
          AUTHORITY["EPSG","4269"]],
      PROJECTION["Transverse_Mercator"],
      PARAMETER["latitude_of_origin",0],
      PARAMETER["central_meridian",-123],
      PARAMETER["scale_factor",0.9996],
      PARAMETER["false_easting",500000],
      PARAMETER["false_northing",0],
      UNIT["metre",1,
          AUTHORITY["EPSG","9001"]],
      AXIS["Easting",EAST],
      AXIS["Northing",NORTH],
      AUTHORITY["EPSG","26910"]]
  Merging duplicate points in ways
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format test1.osm | diff -uNr - $TESTDIR/version.xml

timestamp:
  $ ogr2pbf --osm -f --add-timestamp $TESTDIR/shapefiles/test1.shp
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  PROJCS["NAD83 / UTM zone 10N",
      GEOGCS["NAD83",
          DATUM["North_American_Datum_1983",
              SPHEROID["GRS 1980",6378137,298.257222101,
                  AUTHORITY["EPSG","7019"]],
              AUTHORITY["EPSG","6269"]],
          PRIMEM["Greenwich",0,
              AUTHORITY["EPSG","8901"]],
          UNIT["degree",0.0174532925199433,
              AUTHORITY["EPSG","9122"]],
          AUTHORITY["EPSG","4269"]],
      PROJECTION["Transverse_Mercator"],
      PARAMETER["latitude_of_origin",0],
      PARAMETER["central_meridian",-123],
      PARAMETER["scale_factor",0.9996],
      PARAMETER["false_easting",500000],
      PARAMETER["false_northing",0],
      UNIT["metre",1,
          AUTHORITY["EPSG","9001"]],
      AXIS["Easting",EAST],
      AXIS["Northing",NORTH],
      AUTHORITY["EPSG","26910"]]
  Merging duplicate points in ways
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ cp test1.osm $TESTDIR/check_manual_timestamp.osm

duplicatewaynodes:
  $ ogr2pbf --osm -f $TESTDIR/shapefiles/duplicate-way-nodes.gml
  Using default translations
  Preparing to convert .* (re)
  Layer has no projection metadata, falling back to EPSG:4326
  Detected projection metadata:
  PROJCS["Amersfoort / RD New",
      GEOGCS["Amersfoort",
          DATUM["Amersfoort",
              SPHEROID["Bessel 1841",6377397.155,299.1528128,
                  AUTHORITY["EPSG","7004"]],
              AUTHORITY["EPSG","6289"]],
          PRIMEM["Greenwich",0,
              AUTHORITY["EPSG","8901"]],
          UNIT["degree",0.0174532925199433,
              AUTHORITY["EPSG","9122"]],
          AUTHORITY["EPSG","4289"]],
      PROJECTION["Oblique_Stereographic"],
      PARAMETER["latitude_of_origin",52.1561605555556],
      PARAMETER["central_meridian",5.38763888888889],
      PARAMETER["scale_factor",0.9999079],
      PARAMETER["false_easting",155000],
      PARAMETER["false_northing",463000],
      UNIT["metre",1,
          AUTHORITY["EPSG","9001"]],
      AXIS["Easting",EAST],
      AXIS["Northing",NORTH],
      AUTHORITY["EPSG","28992"]]
  Unhandled geometry, type 10
  Detected projection metadata:
  PROJCS["Amersfoort / RD New",
      GEOGCS["Amersfoort",
          DATUM["Amersfoort",
              SPHEROID["Bessel 1841",6377397.155,299.1528128,
                  AUTHORITY["EPSG","7004"]],
              AUTHORITY["EPSG","6289"]],
          PRIMEM["Greenwich",0,
              AUTHORITY["EPSG","8901"]],
          UNIT["degree",0.0174532925199433,
              AUTHORITY["EPSG","9122"]],
          AUTHORITY["EPSG","4289"]],
      PROJECTION["Oblique_Stereographic"],
      PARAMETER["latitude_of_origin",52.1561605555556],
      PARAMETER["central_meridian",5.38763888888889],
      PARAMETER["scale_factor",0.9999079],
      PARAMETER["false_easting",155000],
      PARAMETER["false_northing",463000],
      UNIT["metre",1,
          AUTHORITY["EPSG","9001"]],
      AXIS["Easting",EAST],
      AXIS["Northing",NORTH],
      AUTHORITY["EPSG","28992"]]
  Merging duplicate points in ways
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format duplicate-way-nodes.osm | diff -uNr - $TESTDIR/duplicate-way-nodes.xml

