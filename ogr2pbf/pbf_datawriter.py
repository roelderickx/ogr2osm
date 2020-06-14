# -*- coding: utf-8 -*-

import logging, sys, os, zlib

from .osm_geometries import OsmId, OsmPoint, OsmWay, OsmRelation
from .datawriter_base_class import DataWriterBase

import ogr2pbf.fileformat_pb2 as fileprotobuf
import ogr2pbf.osmformat_pb2 as osmprotobuf

# https://wiki.openstreetmap.org/wiki/PBF_Format

class PbfPrimitiveGroup:
    def __init__(self):
        self.stringtable = {}
        self._add_string("")
        
        self.granularity = 100
        self.lat_offset = 0
        self.lon_offset = 0
        self.date_granularity = 1000
        
        self.primitive_group = osmprotobuf.PrimitiveGroup()
    
    
    def _add_string(self, s):
        if not s in self.stringtable:
            index = len(self.stringtable)
            self.stringtable[s] = index
            return index
        else:
            return self.stringtable[s]



class PbfPrimitiveGroupDenseNodes(PbfPrimitiveGroup):
    def __init__(self):
        super(PbfPrimitiveGroupDenseNodes, self).__init__()
        
        self.__last_id = 0
        self.__last_lat = 0
        self.__last_lon = 0
    
    
    def __lat_to_pbf(self, lat):
        return int((lat * 1e9 - self.lat_offset) / self.granularity)
    
    
    def __lon_to_pbf(self, lon):
        return int((lon * 1e9 - self.lon_offset) / self.granularity)
    
    
    def add_node(self, osmpoint):
        pbflat = self.__lat_to_pbf(osmpoint.y)
        pbflon = self.__lon_to_pbf(osmpoint.x)

        self.primitive_group.dense.id.append(osmpoint.id - self.__last_id)
        self.primitive_group.dense.lat.append(pbflat - self.__last_lat)
        self.primitive_group.dense.lon.append(pbflon - self.__last_lon)
        
        self.__last_id = osmpoint.id
        self.__last_lat = pbflat
        self.__last_lon = pbflon
        
        for (key, value) in osmpoint.tags.items():
            self.primitive_group.dense.keys_vals.append(self._add_string(key))
            self.primitive_group.dense.keys_vals.append(self._add_string(value))
        self.primitive_group.dense.keys_vals.append(0)



class PbfPrimitiveGroupWays(PbfPrimitiveGroup):
    def __init__(self):
        super(PbfPrimitiveGroupWays, self).__init__()
        
    
    def add_way(self, osmway):
        way = osmprotobuf.Way()
        way.id = osmway.id
        
        for (key, value) in osmway.tags.items():
            way.keys.append(self._add_string(key))
            way.vals.append(self._add_string(value))
        
        prev_node_id = 0
        for node in osmway.points:
            way.refs.append(node.id - prev_node_id)
            prev_node_id = node.id
        
        self.primitive_group.ways.append(way)
    
    

class PbfPrimitiveGroupRelations(PbfPrimitiveGroup):
    def __init__(self):
        super(PbfPrimitiveGroupRelations, self).__init__()
        
    
    def add_relation(self, osmrelation):
        relation = osmprotobuf.Relation()
        relation.id = osmrelation.id
        
        for (key, value) in osmrelation.tags.items():
            relation.keys.append(self._add_string(key))
            relation.vals.append(self._add_string(value))
        
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
        
        self.primitive_group.relations.append(relation)



class PbfDataWriter(DataWriterBase):
    def __init__(self, filename, pbf_no_zlib=False):
       self.filename = filename
       self.pbf_no_zlib = pbf_no_zlib
    
    
    def open(self):
        self.f = open(self.filename, 'wb', buffering = -1)
    
    
    def __write_blob(self, data, block_type):
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
        
        header_block = osmprotobuf.HeaderBlock()
        header_block.required_features.append("OsmSchema-V0.6")
        header_block.required_features.append("DenseNodes")
        header_block.writingprogram = "ogr2pbf %s" % self.get_version()
        self.__write_blob(header_block.SerializeToString(), "OSMHeader")


    def __write_primitive_block(self, pbf_primitive_group):
        logging.debug("Primitive block generation")
        
        primitive_block = osmprotobuf.PrimitiveBlock()
        # add stringtable
        for (string, index) in sorted(pbf_primitive_group.stringtable.items(), key=lambda kv: kv[1]):
            primitive_block.stringtable.s.append(string.encode('utf-8'))
        # add geometries
        primitive_block.primitivegroup.append(pbf_primitive_group.primitive_group)
        # set parameters
        primitive_block.granularity = pbf_primitive_group.granularity
        primitive_block.lat_offset = pbf_primitive_group.lat_offset
        primitive_block.lon_offset = pbf_primitive_group.lon_offset
        primitive_block.date_granularity = pbf_primitive_group.date_granularity
        # write primitive block
        self.__write_blob(primitive_block.SerializeToString(), "OSMData")

    
    def write_nodes(self, nodes):
        logging.debug("Writing nodes")
        primitive_group = PbfPrimitiveGroupDenseNodes()
        for node in nodes:
            primitive_group.add_node(node)
        self.__write_primitive_block(primitive_group)
    
    
    def write_ways(self, ways):
        logging.debug("Writing ways")
        primitive_group = PbfPrimitiveGroupWays()
        for way in ways:
            primitive_group.add_way(way)
        self.__write_primitive_block(primitive_group)
    
    
    def write_relations(self, relations):
        logging.debug("Writing relations")
        primitive_group = PbfPrimitiveGroupRelations()
        for relation in relations:
            primitive_group.add_relation(relation)
        self.__write_primitive_block(primitive_group)
    
    
    def close(self):
        if self.f:
            self.f.close()
            self.f = None

