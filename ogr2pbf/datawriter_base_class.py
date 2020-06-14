# -*- coding: utf-8 -*-

from .version import __version__

'''
ogr2pbf will do the following, given an instance dw of class DataWriterBase:

    dw.open()
    try:
        dw.write_header()
        dw.write_nodes(node_list)
        dw.write_ways(way_list)
        dw.write_relations(relation_list)
        dw.write_footer()
    finally:
        dw.close()
'''

class DataWriterBase:
    def __init__(self):
        pass
    
    
    def get_version(self):
        return __version__
    
    
    def open(self):
        pass
    
    
    def write_header(self):
        pass
    
    
    def write_nodes(self, nodes):
        pass
    
    
    def write_ways(self, ways):
        pass
    
    
    def write_relations(self, relations):
        pass
    
    
    def write_footer(self):
        pass
    
    
    def close(self):
        pass

