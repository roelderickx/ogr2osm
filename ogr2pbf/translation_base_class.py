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
    # note 1: fieldNames parameter has been removed, but can be recovered from ogrfeature:
    # ---
    # feature_def = ogrfeature.GetDefnRef()
    # field_names = []
    # for i in range(feature_def.GetFieldCount()):
    #     field_names.append(feature_def.GetFieldDefn(i).GetNameRef())
    # ---
    # note 2: reproject is a function to convert the feature to 4326 projection with coordnates
    # in traditional gis order. However, do not return the reprojected feature as it will be
    # done again in ogr2osm
    def filter_feature(self, ogrfeature, reproject):
        return ogrfeature
    
    
    # Override this method if you want to modify ar add tags to the xml output
    def filter_tags(self, tags):
        return tags
    
    
    # This method is called after the creation of an OsmGeometry object. The ogr feature
    # and ogr geometry used to create the object are passed as well. Note that any return
    # values will be discarded by ogr2osm.
    def process_feature_post(self, osmgeometry, ogrfeature, ogrgeometry):
        pass
    
    
    # Override this method if you want to modify the list of OsmGeometry objects,
    # or take any additional actions right before writing the objects to the OSM file.
    # Note that any return values will be discarded by ogr2osm.
    def process_output(self, osmgeometries):
        pass

