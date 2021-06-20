  $ [ "$0" != "/bin/bash" ] || shopt -s expand_aliases
  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ alias ogr2osm="PYTHONPATH=$TESTDIR/.. $PYTHON -m ogr2osm"

basicgeometries:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/basic_geometries.kml
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

