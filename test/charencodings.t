  $ [ "$0" != "/bin/bash" ] || shopt -s expand_aliases
  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ alias ogr2osm="PYTHONPATH=$TESTDIR/.. $PYTHON -m ogr2osm"

utf8:
  $ ogr2osm -f $TESTDIR/shapefiles/sp_usinas.shp
  Using default translations
  Preparing to convert .* (re)
  Detected projection metadata:
  GEOGCS["SAD69",
      DATUM["South_American_Datum_1969",
          SPHEROID["GRS 1967 Modified",6378160,298.25,
              AUTHORITY["EPSG","7050"]],
          AUTHORITY["EPSG","6618"]],
      PRIMEM["Greenwich",0,
          AUTHORITY["EPSG","8901"]],
      UNIT["degree",0.0174532925199433,
          AUTHORITY["EPSG","9122"]],
      AXIS["Latitude",NORTH],
      AXIS["Longitude",EAST],
      AUTHORITY["EPSG","4618"]]
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format sp_usinas.osm | diff -uNr - $TESTDIR/utf8.xml

japanese:
  $ ogr2osm --encoding shift_jis --gis-order -f $TESTDIR/shapefiles/japanese.shp
  Using default translations
  Preparing to convert .* (re)
  Layer has no projection metadata, falling back to EPSG:4326
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  Writing file footer
  $ xmllint --format japanese.osm | diff -uNr - $TESTDIR/japanese.xml

