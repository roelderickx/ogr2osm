# -*- coding: utf-8 -*-

import logging
from datetime import datetime

class OsmDataWriter:
    def __init__(self, filename, never_upload=False, no_upload_false=False, never_download=False, \
                 locked=False, add_version=False, add_timestamp=False):
        self.filename = filename
        self.never_upload = never_upload
        self.no_upload_false = no_upload_false
        self.never_download = never_download
        self.locked = locked
        self.add_version = add_version
        self.add_timestamp = add_timestamp
        #self.gzip_compression_level = gzip_compression_level
    
    
    def write(self, geometries):
        logging.debug("Outputting OSM")

        #openfile = lambda: None
        #if 0 < self.gzip_compression_level < 10:
        #    import gzip
        #    openfile = lambda: gzip.open(self.filename, "wb", self.gzip_compression_level)
        #else:
        #    openfile = lambda: open(self.filename, "w")
        
        # Open up the output file with the system default buffering
        #with openfile() as f:
        with open(self.filename, 'w', buffering = -1) as f:
            f.write('<?xml version="1.0"?>\n')
            f.write('<osm version="0.6" generator="ogr2pbf"')
            if self.never_upload:
                f.write(' upload="never"')
            elif not self.no_upload_false:
                f.write(' upload="false"')
            if self.never_download:
                f.write(' download="never"')
            if self.locked:
                f.write(' locked="true"')
            f.write('>\n')

            # Build up a dict for optional settings
            attributes = {}
            if self.add_version:
                attributes.update({'version':'1'})
            if self.add_timestamp:
                attributes.update({'timestamp':datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')})

            for osmgeometry in sorted(geometries, key = lambda geom: geom.get_xml_order()):
                f.write(osmgeometry.to_xml(attributes))
                f.write('\n')

            f.write('</osm>')
    
    
    def flush(self):
        pass

