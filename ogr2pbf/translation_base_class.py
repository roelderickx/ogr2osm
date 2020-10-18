# -*- coding: utf-8 -*-

class TranslationBase:
    def __init__(self):
        pass
    
    
    # Override this method if you want to modify the given layer,
    # or return None if you want to suppress the layer
    def filter_layer(self, layer):
        return layer
    
    
    # Override this method if you want to modify the given feature,
    # or return None if you want to suppress the feature
    # note 1: layer_fields contains a tuple (index, field_name, field_type)
    # note 2: reproject is a function to convert the feature to 4326 projection
    # with coordinates in traditional gis order. However, do not return the
    # reprojected feature since it will be done again in ogr2pbf.
    def filter_feature(self, ogrfeature, layer_fields, reproject):
        return ogrfeature
    
    
    # Override this method if you want to modify or add tags to the xml output
    def filter_tags(self, tags):
        return tags
    
    
    # This method is used to identify identical nodes for merging. By default
    # only the rounded coordinates are taken into account, but you can extend
    # this with some tags as desired. The return value should be a hashable
    # type, if you don't want to merge you can just return a counter value.
    # note: this function will not be called for nodes belonging to a way,
    # they are always identified by the tuple (rounded_x, rounded_y).
    def get_unique_node_identifier(self, rounded_x, rounded_y, tags):
        return (rounded_x, rounded_y)
    
    
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

