# -*- coding: utf-8 -*-

import logging, time

from .datawriter_base_class import DataWriterBase

class OsmDataWriter(DataWriterBase):
    def __init__(self, filename, never_upload=False, no_upload_false=False, never_download=False, \
                 locked=False, add_version=False, add_timestamp=False):
        self.filename = filename
        self.never_upload = never_upload
        self.no_upload_false = no_upload_false
        self.never_download = never_download
        self.locked = locked
        #self.gzip_compression_level = gzip_compression_level
        self.f = None

        # Build up a dict for optional settings
        self.attributes = {}
        if add_version:
            self.attributes.update({'version':'1'})
        if add_timestamp:
            self.attributes.update({'timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ')})
    
    
    def open(self):
        #if 0 < self.gzip_compression_level < 10:
        #    import gzip
        #    self.f = gzip.open(self.filename, "wb", self.gzip_compression_level)
        #else:
        #    self.f = open(self.filename, "w", buffering = -1)
        self.f = open(self.filename, 'w', buffering = -1)


    def write_header(self):
        logging.debug("Writing file header")
        
        self.f.write('<?xml version="1.0"?>\n')
        self.f.write('<osm version="0.6" generator="ogr2pbf %s"' % self.get_version())
        if self.never_upload:
            self.f.write(' upload="never"')
        elif not self.no_upload_false:
            self.f.write(' upload="false"')
        if self.never_download:
            self.f.write(' download="never"')
        if self.locked:
            self.f.write(' locked="true"')
        self.f.write('>\n')
    
    
    def __write_geometries(self, geoms):
        for osm_geom in geoms:
            self.f.write(osm_geom.to_xml(self.attributes))
            self.f.write('\n')

    
    def write_nodes(self, nodes):
        logging.debug("Writing nodes")
        self.__write_geometries(nodes)
    
    
    def write_ways(self, ways):
        logging.debug("Writing ways")
        self.__write_geometries(ways)
    
    
    def write_relations(self, relations):
        logging.debug("Writing relations")
        self.__write_geometries(relations)
    
    
    def write_footer(self):
        logging.debug("Writing file footer")
        self.f.write('</osm>')
    
    
    def close(self):
        if self.f:
            self.f.close()
            self.f = None

