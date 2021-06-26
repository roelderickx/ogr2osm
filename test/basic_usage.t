  $ [ "$0" != "/bin/bash" ] || shopt -s expand_aliases
  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ alias ogr2osm="PYTHONPATH=$TESTDIR/.. $PYTHON -m ogr2osm"

usage:
  $ ogr2osm -h
  usage: ogr2osm [-h] [--version] [-t TRANSLATION] [--encoding ENCODING]
                 [--sql SQLQUERY] [--no-memory-copy] [-e EPSG_CODE]
                 [-p PROJ4_STRING] [--gis-order]
                 [--rounding-digits ROUNDINGDIGITS]
                 [--significant-digits SIGNIFICANTDIGITS]
                 [--split-ways MAXNODESPERWAY] [--id ID] [--idfile IDFILE]
                 [--saveid SAVEID] [-o OUTPUT] [-f] [--pbf] [--no-upload-false]
                 [--never-download] [--never-upload] [--locked] [--add-bounds]
                 [--suppress-empty-tags]
                 DATASOURCE
  
  positional arguments:
    DATASOURCE            DATASOURCE can be a file path or a org PostgreSQL
                          connection string such as: "PG:dbname=pdx_bldgs
                          user=emma host=localhost" (including the quotes)
  
  optional arguments:
    -h, --help            show this help message and exit
    --version             show program's version number and exit
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
    --rounding-digits ROUNDINGDIGITS
                          Number of decimal places for rounding when snapping
                          nodes together (default: 7)
    --significant-digits SIGNIFICANTDIGITS
                          Number of decimal places for coordinates to output
                          (default: 9)
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
    --pbf                 Write the output as a PBF file in stead of an OSM file
    --no-upload-false     Omit upload=false from the completed file to suppress
                          JOSM warnings when uploading.
    --never-download      Prevent JOSM from downloading more data to this file.
    --never-upload        Completely disables all upload commands for this file
                          in JOSM, rather than merely showing a warning before
                          uploading.
    --locked              Prevent any changes to this file in JOSM, such as
                          editing or downloading, and also prevents uploads.
                          Implies upload="never" and download="never".
    --add-bounds          Add boundaries to output file
    --suppress-empty-tags
                          Suppress empty tags

						  
require_output_file_when_using_db_source:
  $ ogr2osm "PG:dbname=test"
  usage: ogr2osm [-h] [--version] [-t TRANSLATION] [--encoding ENCODING]
                 [--sql SQLQUERY] [--no-memory-copy] [-e EPSG_CODE]
                 [-p PROJ4_STRING] [--gis-order]
                 [--rounding-digits ROUNDINGDIGITS]
                 [--significant-digits SIGNIFICANTDIGITS]
                 [--split-ways MAXNODESPERWAY] [--id ID] [--idfile IDFILE]
                 [--saveid SAVEID] [-o OUTPUT] [-f] [--pbf] [--no-upload-false]
                 [--never-download] [--never-upload] [--locked] [--add-bounds]
                 [--suppress-empty-tags]
                 DATASOURCE
  ogr2osm: error: ERROR: An output file must be explicitly specified when using a database source
  [2]

require_query_when_using_db_source:
  $ ogr2osm "PG:dbname=test" -o test.osm
  usage: ogr2osm [-h] [--version] [-t TRANSLATION] [--encoding ENCODING]
                 [--sql SQLQUERY] [--no-memory-copy] [-e EPSG_CODE]
                 [-p PROJ4_STRING] [--gis-order]
                 [--rounding-digits ROUNDINGDIGITS]
                 [--significant-digits SIGNIFICANTDIGITS]
                 [--split-ways MAXNODESPERWAY] [--id ID] [--idfile IDFILE]
                 [--saveid SAVEID] [-o OUTPUT] [-f] [--pbf] [--no-upload-false]
                 [--never-download] [--never-upload] [--locked] [--add-bounds]
                 [--suppress-empty-tags]
                 DATASOURCE
  ogr2osm: error: ERROR: You must specify a query with --sql when using a database source
  [2]

require_db_source_for_sql_query:
  $ rm -f basic_geometries.osm
  $ ogr2osm $TESTDIR/shapefiles/basic_geometries.kml --sql="SELECT * FROM wombats"
  WARNING: You specified a query with --sql but you are not using a database source
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  GEOGCS["WGS 84",
      DATUM["WGS_1984",
          SPHEROID["WGS 84",6378137,298.257223563,
              AUTHORITY["EPSG","7030"]],
          AUTHORITY["EPSG","6326"]],
      PRIMEM["Greenwich",0,
          AUTHORITY["EPSG","8901"]],
      UNIT["degree",0.0174532925199433,
          AUTHORITY["EPSG","9122"]],
      AXIS["Latitude",NORTH],
      AXIS["Longitude",EAST],
      AUTHORITY["EPSG","4326"]]
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/basic_geometries.xml

duplicatefile:
  $ ogr2osm $TESTDIR/shapefiles/basic_geometries.kml
  usage: ogr2osm [-h] [--version] [-t TRANSLATION] [--encoding ENCODING]
                 [--sql SQLQUERY] [--no-memory-copy] [-e EPSG_CODE]
                 [-p PROJ4_STRING] [--gis-order]
                 [--rounding-digits ROUNDINGDIGITS]
                 [--significant-digits SIGNIFICANTDIGITS]
                 [--split-ways MAXNODESPERWAY] [--id ID] [--idfile IDFILE]
                 [--saveid SAVEID] [-o OUTPUT] [-f] [--pbf] [--no-upload-false]
                 [--never-download] [--never-upload] [--locked] [--add-bounds]
                 [--suppress-empty-tags]
                 DATASOURCE
  ogr2osm: error: ERROR: output file '.*basic_geometries.osm' exists (re)
  [2]

force:
  $ ogr2osm -f $TESTDIR/shapefiles/basic_geometries.kml
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  GEOGCS["WGS 84",
      DATUM["WGS_1984",
          SPHEROID["WGS 84",6378137,298.257223563,
              AUTHORITY["EPSG","7030"]],
          AUTHORITY["EPSG","6326"]],
      PRIMEM["Greenwich",0,
          AUTHORITY["EPSG","8901"]],
      UNIT["degree",0.0174532925199433,
          AUTHORITY["EPSG","9122"]],
      AXIS["Latitude",NORTH],
      AXIS["Longitude",EAST],
      AUTHORITY["EPSG","4326"]]
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/basic_geometries.xml

nomemorycopy:
  $ ogr2osm -f --no-memory-copy $TESTDIR/shapefiles/basic_geometries.kml
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  GEOGCS["WGS 84",
      DATUM["WGS_1984",
          SPHEROID["WGS 84",6378137,298.257223563,
              AUTHORITY["EPSG","7030"]],
          AUTHORITY["EPSG","6326"]],
      PRIMEM["Greenwich",0,
          AUTHORITY["EPSG","8901"]],
      UNIT["degree",0.0174532925199433,
          AUTHORITY["EPSG","9122"]],
      AXIS["Latitude",NORTH],
      AXIS["Longitude",EAST],
      AUTHORITY["EPSG","4326"]]
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/basic_geometries.xml

