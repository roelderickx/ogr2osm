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
        
        self.__nodes = []
        self.__ways = []
        self.__relations = []
        self.__linestring_points = {}
        self.__long_ways_from_polygons = set()


    # This function builds up a dictionary with the source data attributes
    # and passes them to the filter_tags function, returning the result.
    def __get_feature_tags(self, ogrfeature, source_encoding):
        tags = {}
        feature_def = ogrfeature.GetDefnRef()
        for i in range(feature_def.GetFieldCount()):
            field_name = feature_def.GetFieldDefn(i).GetNameRef()
            field_type = feature_def.GetFieldDefn(i).GetType()
            field_value = ''
            
            if field_type == ogr.OFTString:
                field_value = ogrfeature.GetFieldAsBinary(i).decode(source_encoding)
            else:
                field_value = ogrfeature.GetFieldAsString(i)

            tags[field_name] = field_value.strip()
        
        return self.translation.filter_tags(tags)


    def __trunc_significant(self, n):
        return int(round(n * 10**self.significant_digits)) * 10**-self.significant_digits
    
    
    def __round_number(self, n):
        return int(round(n * 10**self.rounding_digits))
    
    
    def __parse_point(self, ogrgeometry):
        x = self.__trunc_significant(ogrgeometry.GetX())
        y = self.__trunc_significant(ogrgeometry.GetY())
        node = OsmPoint(x, y)
        self.__nodes.append(node)
        return node


    def __parse_linestring(self, ogrgeometry):
        way = OsmWay()
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
                self.__nodes.append(mypoint)
                self.__linestring_points[(rx, ry)] = mypoint
            way.points.append(mypoint)
            mypoint.addparent(way)
        self.__ways.append(way)
        return way


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
            relation = OsmRelation()
            try:
                exterior = self.__parse_linestring(ogrgeometry.GetGeometryRef(0))
                exterior.addparent(relation)
            except:
                logging.warning("Polygon with no exterior ring?")
                return None
            relation.members.append((exterior, "outer"))
            for i in range(1, ogrgeometry.GetGeometryCount()):
                interior = self.__parse_linestring(ogrgeometry.GetGeometryRef(i))
                interior.addparent(relation)
                relation.members.append((interior, "inner"))
            self.__relations.append(relation)
            return relation


    def __parse_collection(self, ogrgeometry):
        # OGR MultiPolygon maps easily to osm multipolygon, so special case it
        # TODO: Does anything else need special casing?
        geometry_type = ogrgeometry.GetGeometryType()
        if geometry_type in [ ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D ]:
            if ogrgeometry.GetGeometryCount() > 1:
                relation = OsmRelation()
                for polygon in range(ogrgeometry.GetGeometryCount()):
                    ext_geom = ogrgeometry.GetGeometryRef(polygon).GetGeometryRef(0)
                    exterior = self.__parse_linestring(ext_geom)
                    exterior.addparent(relation)
                    relation.members.append((exterior, "outer"))
                    for i in range(1, ogrgeometry.GetGeometryRef(polygon).GetGeometryCount()):
                        int_geom = ogrgeometry.GetGeometryRef(polygon).GetGeometryRef(i)
                        interior = self.__parse_linestring(int_geom)
                        interior.addparent(relation)
                        relation.members.append((interior, "inner"))
                self.__relations.append(relation)
                return [ relation ]
            else:
               return [ self.__parse_polygon(ogrgeometry.GetGeometryRef(0)) ]
        elif geometry_type in [ ogr.wkbMultiLineString, ogr.wkbMultiLineString25D ]:
            geometries = []
            for linestring in range(ogrgeometry.GetGeometryCount()):
                geometries.append(self.__parse_linestring(ogrgeometry.GetGeometryRef(linestring)))
            return geometries
        else:
            relation = OsmRelation()
            for i in range(ogrgeometry.GetGeometryCount()):
                member = self.__parse_geometry(ogrgeometry.GetGeometryRef(i))
                member.addparent(relation)
                relation.members.append((member, "member"))
            self.__relations.append(relation)
            return [ relation ]
    
    
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


    def add_feature(self, ogrfeature, source_encoding, reproject = lambda geometry: None):
        if ogrfeature is None:
            return
        
        ogrfilteredfeature = self.translation.filter_feature(ogrfeature, reproject)
        if ogrfilteredfeature is None:
            return
        
        ogrgeometry = ogrfilteredfeature.GetGeometryRef()
        if ogrgeometry is None:
            return
        
        feature_tags = self.__get_feature_tags(ogrfilteredfeature, source_encoding)
        reproject(ogrgeometry)
        osmgeometries = self.__parse_geometry(ogrgeometry)

        for osmgeometry in [ geom for geom in osmgeometries if geom ]:
            osmgeometry.add_tags(feature_tags)
            
            self.translation.process_feature_post(osmgeometry, ogrfilteredfeature, ogrgeometry)


    def merge_points(self):
        logging.debug("Merging points")

        # Make list of Points at each location
        logging.debug("Making list")
        pointcoords = {}
        for i in self.__nodes:
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
                        self.__nodes.remove(point)


    def merge_way_points(self):
        logging.debug("Merging duplicate points in ways")

        # Remove duplicate points from ways,
        # a duplicate has the same id as its predecessor
        for way in self.__ways:
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
                    self.__ways.append(new_way)

        for new_way, points in zip(new_ways, new_points):
            new_way.points = points
            if new_way.id != way.id:
                for point in points:
                    point.removeparent(way)
                    point.addparent(new_way)

        return new_ways


    def __merge_into_new_relation(self, way_parts):
        new_relation = OsmRelation()
        self.__relations.append(new_relation)
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

        for way in self.__ways:
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
                        self.add_feature(ogrfeature, datasource.source_encoding, reproject)

        self.merge_points()
        self.merge_way_points()
        self.split_long_ways()


    class DataWriterContextManager:
        def __init__(self, datawriter):
            self.datawriter = datawriter
        
        def __enter__(self):
            self.datawriter.open()
            return self.datawriter
        
        def __exit__(self, exception_type, value, traceback):
            self.datawriter.close()


    def output(self, datawriter):
        self.translation.process_output(self.__nodes, self.__ways, self.__relations)
        
        with self.DataWriterContextManager(datawriter) as dw:
            dw.write_header()
            dw.write_nodes(self.__nodes)
            dw.write_ways(self.__ways)
            dw.write_relations(self.__relations)
            dw.write_footer()

