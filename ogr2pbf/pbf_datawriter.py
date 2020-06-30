# -*- coding: utf-8 -*-

import logging, sys, time, zlib

from .osm_geometries import OsmId, OsmPoint, OsmWay, OsmRelation
from .datawriter_base_class import DataWriterBase

import ogr2pbf.fileformat_pb2 as fileprotobuf
import ogr2pbf.osmformat_pb2 as osmprotobuf

# https://wiki.openstreetmap.org/wiki/PBF_Format

class PbfPrimitiveGroup:
    def __init__(self, add_version, add_timestamp):
        self.stringtable = {}
        self._add_string("")
        
        self._add_version = add_version
        self._version = -1
        if self._add_version:
            self._version = 1
        self._add_timestamp = add_timestamp
        self._timestamp = time.localtime(-1)
        if self._add_timestamp:
            self._timestamp = time.localtime()
        
        self.granularity = 100
        self.lat_offset = 0
        self.lon_offset = 0
        self.date_granularity = 1000
        
        self.primitive_group = osmprotobuf.PrimitiveGroup()
    
    
    # add string s to the stringtable if not yet present and returns index
    def _add_string(self, s):
        if not s in self.stringtable:
            index = len(self.stringtable)
            self.stringtable[s] = index
            return index
        else:
            return self.stringtable[s]
    
    
    # convert given latitude to value used in pbf
    def _lat_to_pbf(self, lat):
        return int((lat * 1e9 - self.lat_offset) / self.granularity)
    
    
    # convert given longitude to value used in pbf
    def _lon_to_pbf(self, lon):
        return int((lon * 1e9 - self.lon_offset) / self.granularity)
    
    
    # convert time.struct_time to value used in pbf
    def _timestamp_to_pbf(self, timestamp):
        return int(time.mktime(timestamp) * 1000 / self.date_granularity)



class PbfPrimitiveGroupDenseNodes(PbfPrimitiveGroup):
    def __init__(self, add_version, add_timestamp):
        super(PbfPrimitiveGroupDenseNodes, self).__init__(add_version, add_timestamp)
        
        self.__last_id = 0
        self.__last_timestamp = 0
        self.__last_changeset = 0
        self.__last_lat = 0
        self.__last_lon = 0
    
    
    def add_node(self, osmpoint):
        pbftimestamp = self._timestamp_to_pbf(self._timestamp)
        pbfchangeset = 1
        pbflat = self._lat_to_pbf(osmpoint.y)
        pbflon = self._lon_to_pbf(osmpoint.x)

        self.primitive_group.dense.id.append(osmpoint.id - self.__last_id)
        
        # osmosis always requires the whole denseinfo block
        if self._add_version or self._add_timestamp:
            self.primitive_group.dense.denseinfo.version.append(self._version)
            self.primitive_group.dense.denseinfo.timestamp.append(pbftimestamp - self.__last_timestamp)
            self.primitive_group.dense.denseinfo.changeset.append(pbfchangeset - self.__last_changeset)
            self.primitive_group.dense.denseinfo.uid.append(0)
            self.primitive_group.dense.denseinfo.user_sid.append(0)
        
        self.primitive_group.dense.lat.append(pbflat - self.__last_lat)
        self.primitive_group.dense.lon.append(pbflon - self.__last_lon)
        
        self.__last_id = osmpoint.id
        self.__last_timestamp = pbftimestamp
        self.__last_changeset = pbfchangeset
        self.__last_lat = pbflat
        self.__last_lon = pbflon
        
        for (key, value) in osmpoint.tags.items():
            self.primitive_group.dense.keys_vals.append(self._add_string(key))
            self.primitive_group.dense.keys_vals.append(self._add_string(value))
        self.primitive_group.dense.keys_vals.append(0)



class PbfPrimitiveGroupWays(PbfPrimitiveGroup):
    def __init__(self, add_version, add_timestamp):
        super(PbfPrimitiveGroupWays, self).__init__(add_version, add_timestamp)
    
    
    def add_way(self, osmway):
        way = osmprotobuf.Way()
        way.id = osmway.id
        
        for (key, value) in osmway.tags.items():
            way.keys.append(self._add_string(key))
            way.vals.append(self._add_string(value))
        
        # osmosis always requires the whole info block
        if self._add_version or self._add_timestamp:
            way.info.version = self._version
            way.info.timestamp = self._timestamp_to_pbf(self._timestamp)
            way.info.changeset = 1
            way.info.uid = 0
            way.info.user_sid = 0
        
        prev_node_id = 0
        for node in osmway.points:
            way.refs.append(node.id - prev_node_id)
            prev_node_id = node.id
        
        self.primitive_group.ways.append(way)
    
    

class PbfPrimitiveGroupRelations(PbfPrimitiveGroup):
    def __init__(self, add_version, add_timestamp):
        super(PbfPrimitiveGroupRelations, self).__init__(add_version, add_timestamp)
    
    
    def add_relation(self, osmrelation):
        relation = osmprotobuf.Relation()
        relation.id = osmrelation.id
        
        for (key, value) in osmrelation.tags.items():
            relation.keys.append(self._add_string(key))
            relation.vals.append(self._add_string(value))
        
        # osmosis always requires the whole info block
        if self._add_version or self._add_timestamp:
            relation.info.version = self._version
            relation.info.timestamp = self._timestamp_to_pbf(self._timestamp)
            relation.info.changeset = 1
            relation.info.uid = 0
            relation.info.user_sid = 0
        
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
    def __init__(self, filename, add_version=False, add_timestamp=False):
        self.filename = filename
        self.add_version = add_version
        self.add_timestamp = add_timestamp
        
        self.__max_nodes_per_node_block = 8000
        self.__max_node_refs_per_way_block = 32000
        self.__max_member_refs_per_relation_block = 32000
    
    
    def open(self):
        self.f = open(self.filename, 'wb', buffering = -1)
    
    
    def __write_blob(self, data, block_type):
        logging.debug("Writing blob, type = %s" % block_type)
        
        blob = fileprotobuf.Blob()
        blob.raw_size = len(data)
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
        for i in range(0, len(nodes), self.__max_nodes_per_node_block):
            primitive_group = PbfPrimitiveGroupDenseNodes(self.add_version, self.add_timestamp)
            for node in nodes[i:i+self.__max_nodes_per_node_block]:
                primitive_group.add_node(node)
            self.__write_primitive_block(primitive_group)
    
    
    def write_ways(self, ways):
        logging.debug("Writing ways")
        amount_node_refs = 0
        primitive_group = None
        for way in ways:
            if amount_node_refs == 0:
                primitive_group = PbfPrimitiveGroupWays(self.add_version, self.add_timestamp)
            primitive_group.add_way(way)
            amount_node_refs += len(way.points)
            if amount_node_refs > self.__max_node_refs_per_way_block:
                self.__write_primitive_block(primitive_group)
                amount_node_refs = 0
        else:
            if amount_node_refs > 0:
                self.__write_primitive_block(primitive_group)
    
    
    def write_relations(self, relations):
        logging.debug("Writing relations")
        amount_member_refs = 0
        primitive_group = None
        for relation in relations:
            if amount_member_refs == 0:
                primitive_group = PbfPrimitiveGroupRelations(self.add_version, self.add_timestamp)
            primitive_group.add_relation(relation)
            amount_member_refs += len(relation.members)
            if amount_member_refs > self.__max_member_refs_per_relation_block:
                self.__write_primitive_block(primitive_group)
                amount_member_refs = 0
        else:
            if amount_member_refs > 0:
                self.__write_primitive_block(primitive_group)
    
    
    def close(self):
        if self.f:
            self.f.close()
            self.f = None

