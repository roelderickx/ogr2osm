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
  $ osmconvert --drop-author basic_geometries.osm.pbf > basic_geometries.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/basic_geometries.pbf.xml

basicgeometriesduplicate:
  $ ogr2osm --pbf -t $TESTDIR/translations/duplicate-translation.py -f $TESTDIR/shapefiles/basic_geometries_duplicate.kml
  Found valid translation class DuplicateTranslation
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
  Merging tags for duplicate node
  Merging tags for duplicate node
  Merging tags for duplicate node
  Merging tags for duplicate node
  Merging tags for duplicate node
  Merging tags for duplicate node
  Merging tags for duplicate node
  Merging tags for duplicate node
  Merging tags for duplicate node
  Merging tags for duplicate node
  Merging tags for duplicate reverse_way
  Merging tags for duplicate way
  Merging tags for duplicate way
  Merging tags for duplicate way
  Merging tags for duplicate relation
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  $ osmconvert --drop-author basic_geometries.osm.pbf > basic_geometries.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/basic_geometries.pbf.xml

multigeometries:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/multi_geometries.kml
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
  $ osmconvert --drop-author multi_geometries.osm.pbf > multi_geometries.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format multi_geometries.osm | diff -uNr - $TESTDIR/multi_geometries.pbf.xml

multigeometriesduplicate:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/multi_geometries_duplicate.kml
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
  $ osmconvert --drop-author multi_geometries.osm.pbf > multi_geometries.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format multi_geometries.osm | diff -uNr - $TESTDIR/multi_geometries.pbf.xml

collection:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/collection.kml
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
  $ osmconvert --drop-author collection.osm.pbf > collection.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format collection.osm | diff -uNr - $TESTDIR/collection.pbf.xml

collectionduplicate:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/collection_duplicate.kml
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
  $ osmconvert --drop-author collection.osm.pbf > collection.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format collection.osm | diff -uNr - $TESTDIR/collection.pbf.xml

mergetags:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/mergetags.geojson
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
  $ osmconvert --drop-author mergetags.osm.pbf > mergetags.osm 2> /dev/null
  $ xmllint --format mergetags.osm | diff -uNr - $TESTDIR/mergetags.pbf.xml

mergetagsnonempty:
  $ ogr2osm --pbf --suppress-empty-tags -f $TESTDIR/shapefiles/mergetags.geojson
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
  $ osmconvert --drop-author mergetags.osm.pbf > mergetags.osm 2> /dev/null
  $ xmllint --format mergetags.osm | diff -uNr - $TESTDIR/mergetagsnonempty.pbf.xml

tagstoolong:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/tags_too_long.geojson
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
  $ osmconvert --drop-author tags_too_long.osm.pbf > tags_too_long.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format tags_too_long.osm | diff -uNr - $TESTDIR/tags_too_long.pbf.xml

positiveid:
  $ ogr2osm --pbf -f --positive-id $TESTDIR/shapefiles/basic_geometries.kml
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
  $ osmconvert --drop-author basic_geometries.osm.pbf > basic_geometries.osm 2> /dev/null
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/positiveid.pbf.xml

significantdigits:
  $ ogr2osm --pbf -f --significant-digits 5 $TESTDIR/shapefiles/basic_geometries.kml
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
  $ osmconvert --drop-author basic_geometries.osm.pbf > basic_geometries.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/significantdigits.pbf.xml

version:
  $ ogr2osm --pbf -f --add-version $TESTDIR/shapefiles/basic_geometries.kml
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
  $ osmconvert --drop-author basic_geometries.osm.pbf > basic_geometries.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/version.pbf.xml

bounds:
  $ ogr2osm --pbf -f --add-bounds $TESTDIR/shapefiles/basic_geometries.kml
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
  $ osmconvert --drop-author basic_geometries.osm.pbf > basic_geometries.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/bounds.pbf.xml

timestamp:
  $ ogr2osm --pbf -f --add-timestamp $TESTDIR/shapefiles/basic_geometries.kml
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
  $ osmconvert basic_geometries.osm.pbf > $TESTDIR/check_manual_timestamp_from_pbf.osm 2> /dev/null
  \[.[0-9]\] (re)

duplicatewaynodes:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/duplicate-way-nodes.gml
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
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  $ osmconvert --drop-author duplicate-way-nodes.osm.pbf > duplicate-way-nodes.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format duplicate-way-nodes.osm | diff -uNr - $TESTDIR/duplicate-way-nodes.pbf.xml

shapefile:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/testshapefile.shp
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
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  $ osmconvert --drop-author testshapefile.osm.pbf > testshapefile.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format testshapefile.osm | diff -uNr - $TESTDIR/testshapefile.pbf.xml

utf8:
  $ ogr2osm --pbf -f $TESTDIR/shapefiles/utf8.geojson
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
  $ osmconvert --drop-author utf8.osm.pbf > utf8.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format utf8.osm | diff -uNr - $TESTDIR/utf8.pbf.xml

shiftjis:
  $ ogr2osm --pbf --encoding shift_jis --gis-order -f $TESTDIR/shapefiles/shift-jis.geojson
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
  $ osmconvert --drop-author shift-jis.osm.pbf > shift-jis.osm 2> /dev/null
  \[.[0-9]\] (re)
  $ xmllint --format shift-jis.osm | diff -uNr - $TESTDIR/shift-jis.pbf.xml

basicgeometriesfilterlayer:
  $ ogr2osm --pbf -t $TESTDIR/translations/filterlayer-translation.py -f $TESTDIR/shapefiles/basic_geometries.kml
  Found valid translation class FilterLayerTranslation
  Preparing to convert .* (re)
  Splitting long ways
  Writing file header
  Writing nodes
  Writing ways
  Writing relations
  $ osmconvert --drop-author basic_geometries.osm.pbf > basic_geometries.osm 2> /dev/null
  $ xmllint --format basic_geometries.osm | diff -uNr - $TESTDIR/basic_geometries_filterlayer.pbf.xml

