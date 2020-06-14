# -*- coding: utf-8 -*-

import logging, sys, os, zlib

from .osm_geometries import OsmId, OsmPoint, OsmWay, OsmRelation
from .datawriter_base_class import DataWriterBase

import ogr2pbf.fileformat_pb2 as fileprotobuf
import ogr2pbf.osmformat_pb2 as osmprotobuf

# https://wiki.openstreetmap.org/wiki/PBF_Format

class PbfPrimitiveBlock:
    def __init__(self):
        self.stringtable = {}
        self.__add_string("")
        
        self.node_primitive_group = osmprotobuf.PrimitiveGroup()
        self.ways_primitive_group = osmprotobuf.PrimitiveGroup()
        self.relations_primitive_group = osmprotobuf.PrimitiveGroup()
        
        self.granularity = 100
        self.lat_offset = 0
        self.lon_offset = 0
        self.date_granularity = 1000
        
        self.__last_id = 0
        self.__last_lat = 0
        self.__last_lon = 0
    
    
    def __add_string(self, s):
        if not s in self.stringtable:
            index = len(self.stringtable)
            self.stringtable[s] = index
            return index
        else:
            return self.stringtable[s]
    
    
    def __lat_to_pbf(self, lat):
        return int((lat * 1e9 - self.lat_offset) / self.granularity)
    
    
    def __lon_to_pbf(self, lon):
        return int((lon * 1e9 - self.lon_offset) / self.granularity)
    
    
    def add_node(self, osmpoint):
        pbflat = self.__lat_to_pbf(osmpoint.y)
        pbflon = self.__lon_to_pbf(osmpoint.x)

        self.node_primitive_group.dense.id.append(osmpoint.id - self.__last_id)
        self.node_primitive_group.dense.lat.append(pbflat - self.__last_lat)
        self.node_primitive_group.dense.lon.append(pbflon - self.__last_lon)
        
        self.__last_id = osmpoint.id
        self.__last_lat = pbflat
        self.__last_lon = pbflon
        
        for (key, value) in osmpoint.tags.items():
            self.node_primitive_group.dense.keys_vals.append(self.__add_string(key))
            self.node_primitive_group.dense.keys_vals.append(self.__add_string(value))
        self.node_primitive_group.dense.keys_vals.append(0)
    
    
    def add_way(self, osmway):
        way = osmprotobuf.Way()
        way.id = osmway.id
        
        for (key, value) in osmway.tags.items():
            way.keys.append(self.__add_string(key))
            way.vals.append(self.__add_string(value))
        
        prev_node_id = 0
        for node in osmway.points:
            way.refs.append(node.id - prev_node_id)
            prev_node_id = node.id
        
        self.ways_primitive_group.ways.append(way)
    
    
    def add_relation(self, osmrelation):
        relation = osmprotobuf.Relation()
        relation.id = osmrelation.id
        
        for (key, value) in osmrelation.tags.items():
            relation.keys.append(self.__add_string(key))
            relation.vals.append(self.__add_string(value))
        
        prev_member_id = 0
        for member in osmrelation.members:
            relation.memids.append(member.id - prev_member_id)
            prev_member_id = member.id
            
            relation_type = osmprotobuf.MemberType.NODE
            if type(member) == OsmWay:
                relation_type = osmprotobuf.MemberType.WAY
            elif type(member) == OsmRelation:
                relation_type = osmprotobuf.MemberType.RELATION
            relation.types.append(relation_type)
        
        self.relations_primitive_group.relations.append(relation)


    def get_primitive_block(self):
        logging.debug("Primitive block generation")
        primitive_block = osmprotobuf.PrimitiveBlock()
        for (string, index) in sorted(self.stringtable.items(), key=lambda kv: kv[1]):
            primitive_block.stringtable.s.append(string.encode('utf-8'))
        
        primitive_block.primitivegroup.append(self.node_primitive_group)
        primitive_block.primitivegroup.append(self.ways_primitive_group)
        primitive_block.primitivegroup.append(self.relations_primitive_group)
        
        primitive_block.granularity = self.granularity
        primitive_block.lat_offset = self.lat_offset
        primitive_block.lon_offset = self.lon_offset
        primitive_block.date_granularity = self.date_granularity
        
        return primitive_block



class PbfDataWriter(DataWriterBase):
    def __init__(self, filename, pbf_no_zlib=False):
       self.filename = filename
       self.pbf_no_zlib = pbf_no_zlib
    
    
    def open(self):
        self.f = open(self.filename, 'wb', buffering = -1)
    
    
    def __write_blob(self, data, block_type="OSMData"):
        logging.debug("Writing blob, type = %s" % block_type)
        
        blob = fileprotobuf.Blob()
        blob.raw_size = len(data)
        if self.pbf_no_zlib:
            blob.raw = data
        else:
            blob.zlib_data = zlib.compress(data)

        blobheader = fileprotobuf.BlobHeader()
        blobheader.type = block_type
        blobheader.datasize = blob.ByteSize()
        
        blobheaderlen = blobheader.ByteSize().to_bytes(4, byteorder='big')
        self.f.write(blobheaderlen)
        self.f.write(blobheader.SerializeToString())
        self.f.write(blob.SerializeToString())


    def write_header(self):
        logging.debug("Writing file header")
        
        headerblock = osmprotobuf.HeaderBlock()
        headerblock.required_features.append("OsmSchema-V0.6")
        headerblock.required_features.append("DenseNodes")
        headerblock.writingprogram = "ogr2pbf %s" % self.get_version()
        self.__write_blob(headerblock.SerializeToString(), "OSMHeader")

    
    def write_nodes(self, nodes):
        logging.debug("Writing nodes")
        pbf_primitive_block = PbfPrimitiveBlock()
        for node in nodes:
            pbf_primitive_block.add_node(node)
        self.__write_blob(pbf_primitive_block.get_primitive_block().SerializeToString())
    
    
    def write_ways(self, ways):
        logging.debug("Writing ways")
        pbf_primitive_block = PbfPrimitiveBlock()
        for way in ways:
            pbf_primitive_block.add_way(way)
        self.__write_blob(pbf_primitive_block.get_primitive_block().SerializeToString())
    
    
    def write_relations(self, relations):
        logging.debug("Writing relations")
        pbf_primitive_block = PbfPrimitiveBlock()
        for relation in relations:
            pbf_primitive_block.add_relation(relation)
        self.__write_blob(pbf_primitive_block.get_primitive_block().SerializeToString())
    
    
    def close(self):
        if self.f:
            self.f.close()
            self.f = None

