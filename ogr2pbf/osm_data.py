# -*- coding: utf-8 -*-

import logging
from osgeo import ogr
from osgeo import osr

from .osm_geometries import OsmPoint, OsmWay, OsmRelation

class OsmData:
    def __init__(self, translation, significant_digits=9, rounding_digits=7, max_points_in_way=1800):
        # options
        self.translation = translation
        self.significant_digits = significant_digits
        self.rounding_digits = rounding_digits
        self.max_points_in_way = max_points_in_way
        
        self.__geometries = []
        self.__linestring_points = {}
        self.__long_ways_from_polygons = set()


    # This function builds up a dictionary with the source data attributes
    # and passes them to the filter_tags function, returning the result.
    def __get_feature_tags(self, ogrfeature):
        feature_def = ogrfeature.GetDefnRef()
        field_names = []
        for i in range(feature_def.GetFieldCount()):
            field_names.append(feature_def.GetFieldDefn(i).GetNameRef())

        tags = {}
        for j in range(len(field_names)):
            # The field needs to be put into the appropriate encoding and
            # leading or trailing spaces stripped
            tags[field_names[j]] = ogrfeature.GetFieldAsString(j).strip()
        return self.translation.filter_tags(tags)


    def __trunc_significant(self, n):
        return int(round(n * 10**self.significant_digits)) * 10**-self.significant_digits
    
    
    def __round_number(self, n):
        return int(round(n * 10**self.rounding_digits))
    
    
    def __parse_point(self, ogrgeometry):
        x = self.__trunc_significant(ogrgeometry.GetX())
        y = self.__trunc_significant(ogrgeometry.GetY())
        geometry = OsmPoint(x, y)
        self.__geometries.append(geometry)
        return geometry


    def __parse_linestring(self, ogrgeometry):
        geometry = OsmWay()
        # LineString.GetPoint() returns a tuple, so we can't call parsePoint on it
        # and instead have to create the point ourself
        for i in range(ogrgeometry.GetPointCount()):
            (x, y, z_unused) = ogrgeometry.GetPoint(i)
            rx = self.__round_number(x)
            ry = self.__round_number(y)
            if (rx, ry) in self.__linestring_points:
                mypoint = self.__linestring_points[(rx, ry)]
            else:
                mypoint = OsmPoint(self.__trunc_significant(x), self.__trunc_significant(y))
                self.__geometries.append(mypoint)
                self.__linestring_points[(rx, ry)] = mypoint
            geometry.points.append(mypoint)
            mypoint.addparent(geometry)
        self.__geometries.append(geometry)
        return geometry


    def __parse_polygon(self, ogrgeometry):
        # Special case polygons with only one ring. This does not (or at least
        # should not) change behavior when simplify relations is turned on.
        if ogrgeometry.GetGeometryCount() == 0:
            logging.warning("Polygon with no rings?")
        elif ogrgeometry.GetGeometryCount() == 1:
            result = self.__parse_linestring(ogrgeometry.GetGeometryRef(0))
            if len(result.points) > self.max_points_in_way:
                self.__long_ways_from_polygons.add(result)
            return result
        else:
            geometry = OsmRelation()
            try:
                exterior = self.__parse_linestring(ogrgeometry.GetGeometryRef(0))
                exterior.addparent(geometry)
            except:
                logging.warning("Polygon with no exterior ring?")
                return None
            geometry.members.append((exterior, "outer"))
            for i in range(1, ogrgeometry.GetGeometryCount()):
                interior = self.__parse_linestring(ogrgeometry.GetGeometryRef(i))
                interior.addparent(geometry)
                geometry.members.append((interior, "inner"))
            self.__geometries.append(geometry)
            return geometry


    def __parse_collection(self, ogrgeometry):
        # OGR MultiPolygon maps easily to osm multipolygon, so special case it
        # TODO: Does anything else need special casing?
        geometry_type = ogrgeometry.GetGeometryType()
        if geometry_type in [ ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D ]:
            if ogrgeometry.GetGeometryCount() > 1:
                geometry = OsmRelation()
                for polygon in range(ogrgeometry.GetGeometryCount()):
                    ext_geom = ogrgeometry.GetGeometryRef(polygon).GetGeometryRef(0)
                    exterior = self.__parse_linestring(ext_geom)
                    exterior.addparent(geometry)
                    geometry.members.append((exterior, "outer"))
                    for i in range(1, ogrgeometry.GetGeometryRef(polygon).GetGeometryCount()):
                        int_geom = ogrgeometry.GetGeometryRef(polygon).GetGeometryRef(i)
                        interior = self.__parse_linestring(int_geom)
                        interior.addparent(geometry)
                        geometry.members.append((interior, "inner"))
                self.__geometries.append(geometry)
                return [ geometry ]
            else:
               return [ self.__parse_polygon(ogrgeometry.GetGeometryRef(0)) ]
        elif geometry_type in [ ogr.wkbMultiLineString, ogr.wkbMultiLineString25D ]:
            geometries = []
            for linestring in range(ogrgeometry.GetGeometryCount()):
                geometries.append(self.__parse_linestring(ogrgeometry.GetGeometryRef(linestring)))
            return geometries
        else:
            geometry = OsmRelation()
            for i in range(ogrgeometry.GetGeometryCount()):
                member = self.__parse_geometry(ogrgeometry.GetGeometryRef(i))
                member.addparent(geometry)
                geometry.members.append((member, "member"))
            self.__geometries.append(geometry)
            return [ geometry ]
    
    
    def __parse_geometry(self, ogrgeometry):
        osmgeometries = []
        
        geometry_type = ogrgeometry.GetGeometryType()

        if geometry_type in [ ogr.wkbPoint, ogr.wkbPoint25D ]:
            osmgeometries.append(self.__parse_point(ogrgeometry))
        elif geometry_type in [ ogr.wkbLineString, ogr.wkbLinearRing, ogr.wkbLineString25D ]:
            # ogr.wkbLinearRing25D does not exist
            osmgeometries.append(self.__parse_linestring(ogrgeometry))
        elif geometry_type in [ ogr.wkbPolygon, ogr.wkbPolygon25D ]:
            osmgeometries.append(self.__parse_polygon(ogrgeometry))
        elif geometry_type in [ ogr.wkbMultiPoint, ogr.wkbMultiLineString, ogr.wkbMultiPolygon, \
                               ogr.wkbGeometryCollection, ogr.wkbMultiPoint25D, \
                               ogr.wkbMultiLineString25D, ogr.wkbMultiPolygon25D, \
                               ogr.wkbGeometryCollection25D ]:
            osmgeometries.extend(self.__parse_collection(ogrgeometry))
        else:
            logging.warning("Unhandled geometry, type %s" % str(geometry_type))

        return osmgeometries


    def add_feature(self, ogrfeature, reproject = lambda geometry: None):
        if ogrfeature is None:
            return
        
        #reproject = self.__get_reprojection_func(spatial_ref)
        
        ogrfilteredfeature = self.translation.filter_feature(ogrfeature, reproject)
        if ogrfilteredfeature is None:
            return
        
        ogrgeometry = ogrfilteredfeature.GetGeometryRef()
        if ogrgeometry is None:
            return
        
        feature_tags = self.__get_feature_tags(ogrfilteredfeature)
        reproject(ogrgeometry)
        osmgeometries = self.__parse_geometry(ogrgeometry)

        for osmgeometry in [ geom for geom in osmgeometries if geom ]:
            osmgeometry.add_tags(feature_tags)
            
            self.translation.process_feature_post(osmgeometry, ogrfilteredfeature, ogrgeometry)


    def merge_points(self):
        logging.debug("Merging points")
        points = [ geom for geom in self.__geometries if type(geom) == OsmPoint ]

        # Make list of Points at each location
        logging.debug("Making list")
        pointcoords = {}
        for i in points:
            rx = self.__round_number(i.x)
            ry = self.__round_number(i.y)
            if (rx, ry) in pointcoords:
                pointcoords[(rx, ry)].append(i)
            else:
                pointcoords[(rx, ry)] = [i]

        # Use list to get rid of extras
        logging.debug("Checking list")
        for (location, pointsatloc) in pointcoords.items():
            if len(pointsatloc) > 1:
                for point in pointsatloc[1:]:
                    for parent in set(point.get_parents()):
                        parent.replacejwithi(pointsatloc[0], point)
                    if len(point.get_parents()) == 0:
                        self.__geometries.remove(point)


    def merge_way_points(self):
        logging.debug("Merging duplicate points in ways")
        ways = [ geom for geom in self.__geometries if type(geom) == OsmWay ]

        # Remove duplicate points from ways,
        # a duplicate has the same id as its predecessor
        for way in ways:
            previous_id = None
            merged_points = []

            for node in way.points:
                if previous_id == None or previous_id != node.id:
                    merged_points.append(node)
                    previous_id = node.id

            if len(merged_points) > 0:
                way.points = merged_points
            else:
                # TODO delete way? also delete from parent relation?
                pass


    def __split_way(self, way, is_way_in_relation):
        new_points = [ way.points[i:i + self.max_points_in_way] \
                               for i in range(0, len(way.points), self.max_points_in_way - 1) ]
        new_ways = [ way ] + [ OsmWay() for i in range(len(new_points) - 1) ]

        if not is_way_in_relation:
            way_tags = way.tags

            for new_way in new_ways:
                if new_way != way:
                    new_way.add_tags(way_tags)
                    self.__geometries.append(new_way)

        for new_way, points in zip(new_ways, new_points):
            new_way.points = points
            if new_way.id != way.id:
                for point in points:
                    point.removeparent(way)
                    point.addparent(new_way)

        return new_ways


    def __merge_into_new_relation(self, way_parts):
        new_relation = OsmRelation()
        self.__geometries.append(new_relation)
        new_relation.members = [ (way, "outer") for way in way_parts ]
        for way in way_parts:
            way.addparent(new_relation)


    def __split_way_in_relation(self, rel, way_parts):
        way_roles = [ m[1] for m in rel.members if m[0] == way_parts[0] ]
        way_role = "" if len(way_roles) == 0 else way_roles[0]
        for way in way_parts[1:]:
            rel.members.append((way, way_role))


    def split_long_ways(self):
        if self.max_points_in_way < 2:
            # pointless :-)
            return
        
        logging.debug("Splitting long ways")
        ways = [ geom for geom in self.__geometries if type(geom) == OsmWay ]

        for way in ways:
            is_way_in_relation = len([ p for p in way.get_parents() if type(p) == OsmRelation ]) > 0
            if len(way.points) > self.max_points_in_way:
                way_parts = self.__split_way(way, is_way_in_relation)
                if not is_way_in_relation:
                    if way in self.__long_ways_from_polygons:
                        self.__merge_into_new_relation(way_parts)
                else:
                    for rel in way.get_parents():
                        self.__split_way_in_relation(rel, way_parts)


    def process(self, datasource):
        for i in range(datasource.get_layer_count()):
            (layer, reproject) = datasource.get_layer(i)
            
            if layer:
                for i in range(layer.GetFeatureCount()):
                    ogrfeature = layer.GetNextFeature()
                    
                    if ogrfeature:
                        self.add_feature(ogrfeature, reproject)

        self.merge_points()
        self.merge_way_points()
        self.split_long_ways()


    def output(self, datawriter):
        logging.debug("Outputting OSM data")
        
        self.translation.process_output(self.__geometries)
        datawriter.write(self.__geometries)
        datawriter.flush()

