#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' ogr2pbf

This program takes any vector data understandable by OGR and outputs an OSM or
PDF file with that data.

By default tags will be naively copied from the input data. Hooks are provided
so that, with a little python programming, you can translate the tags however
you like. More hooks are provided so you can filter or even modify the features
themselves.

To use the hooks, create a file in the translations/ directory called myfile.py
and run ogr2osm.py -t myfile. This file should define a function with the name
of each hook you want to use. For an example, see the uvmtrans.py file.

The program will use projection metadata from the source, if it has any. If
there is no projection information, or if you want to override it, you can use
-e or -p to specify an EPSG code or Proj.4 string, respectively. If there is no
projection metadata and you do not specify one, EPSG:4326 will be used (WGS84
latitude-longitude)

For additional usage information, run ogr2pbf --help

Copyright (c) 2020 Roel Derickx <roel.derickx AT gmail>

Based on ogr2osm:
Copyright (c) 2012-2013 Paul Norman <penorman@mac.com>, Sebastiaan Couwenberg
<sebastic@xs4all.nl>, The University of Vermont <andrew.guertin@uvm.edu>

Released under the MIT license: http://opensource.org/licenses/mit-license.php

ogr2osm is based very heavily on code released under the following terms:
(c) Iván Sánchez Ortega, 2009
<ivan@sanchezortega.es>
###############################################################################
#  "THE BEER-WARE LICENSE":                                                   #
#  <ivan@sanchezortega.es> wrote this file. As long as you retain this notice #
#  you can do whatever you want with this stuff. If we meet some day, and you #
#  think this stuff is worth it, you can buy me a beer in return.             #
###############################################################################
'''

import sys, os, argparse, logging, inspect
from datetime import datetime

from translation_base_class import TranslationBase
from ogr_datasource import OgrDatasource
from osm_geometries import OsmId, OsmGeometry, OsmPoint, OsmWay, OsmRelation
from osm_data import OsmData

import zlib
import fileformat_pb2 as fileprotobuf
import osmformat_pb2 as osmprotobuf

logging.basicConfig(format="%(message)s", level = logging.DEBUG)


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
    
    
    def __add_node(self, osmpoint):
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
    
    
    def __add_way(self, osmway):
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
    
    
    def __add_relation(self, osmrelation):
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
    
    
    def add_geometry(self, geometry):
        if type(geometry) == OsmPoint:
            self.__add_node(geometry)
        elif type(geometry) == OsmWay:
            self.__add_way(geometry)
        elif type(geometry) == OsmRelation:
            self.__add_relation(geometry)


    def get_primitive_block(self):
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



# https://wiki.openstreetmap.org/wiki/PBF_Format
class PbfDataWriter:
    def __init__(self, filename):
       self.filename = filename
    
    
    def __write_block(self, f, block, block_type="OSMData"):
        blob = fileprotobuf.Blob()
        blob.raw_size = len(block)
        blob.zlib_data = zlib.compress(block)
        
        blobheader = fileprotobuf.BlobHeader()
        blobheader.type = block_type
        blobheader.datasize = blob.ByteSize()
        
        blobheaderlen = blobheader.ByteSize().to_bytes(4, byteorder='big')
        f.write(blobheaderlen)
        f.write(blobheader.SerializeToString())
        f.write(blob.SerializeToString())
    
    
    def write(self, geometries):
        logging.debug("Outputting PBF")

        with open(self.filename, "wb") as f:
            headerblock = osmprotobuf.HeaderBlock()
            headerblock.required_features.append("OsmSchema-V0.6")
            headerblock.required_features.append("DenseNodes")
            headerblock.writingprogram = "ogr2pbf"
            self.__write_block(f, headerblock.SerializeToString(), "OSMHeader")

            pbf_primitive_block = PbfPrimitiveBlock()
            for osmgeometry in sorted(geometries, key = lambda geom: geom.get_xml_order()):
                pbf_primitive_block.add_geometry(osmgeometry)
            
            self.__write_block(f, pbf_primitive_block.get_primitive_block().SerializeToString())


    def flush(self):
        pass



def parse_commandline():
    parser = argparse.ArgumentParser()
    
    #parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")
    #parser.add_argument("-d", "--debug-tags", dest="debugTags", action="store_true",
    #                    help="Output the tags for every feature parsed.")
    parser.add_argument("-t", "--translation", dest="translationmodule",
                        metavar="TRANSLATION",
                        help="Select the attribute-tags translation method. See " +
                             "the translations/ directory for valid values.")
    # datasource options
    parser.add_argument("--encoding", dest="encoding",
                        help="Encoding of the source file. If specified, overrides " +
                             "the default of %(default)s", default="utf-8")
    parser.add_argument("--sql", dest="sqlQuery", type=str, default=None,
                        help="SQL query to execute on a PostgreSQL source")
    parser.add_argument("--no-memory-copy", dest="noMemoryCopy", action="store_true",
                        help="Do not make an in-memory working copy")
    # input projection parameters
    parser.add_argument("-e", "--epsg", dest="sourceEPSG", type=int, metavar="EPSG_CODE",
                        help="EPSG code of source file. Do not include the " +
                             "'EPSG:' prefix. If specified, overrides projection " +
                             "from source metadata if it exists.")
    parser.add_argument("-p", "--proj4", dest="sourcePROJ4", type=str, metavar="PROJ4_STRING",
                        help="PROJ.4 string. If specified, overrides projection " +
                             "from source metadata if it exists.")
    # precision options
    parser.add_argument("--significant-digits", dest="significantDigits", type=int,
                        help="Number of decimal places for coordinates to output " +
                             "(default: %(default)s)",
                        default=9)
    parser.add_argument("--rounding-digits", dest="roundingDigits", type=int,
                        help="Number of decimal places for rounding when snapping " +
                             "nodes together (default: %(default)s)",
                        default=7)
    # transformation options
    parser.add_argument("--split-ways", dest="maxNodesPerWay", type=int, default=1800,
                        help="Split ways with more than the specified number of nodes. " +
                             "Defaults to %(default)s. Any value below 2 - do not split.")
    # ID generation options
    parser.add_argument("--id", dest="id", type=int, default=0,
                        help="ID to start counting from for the output file. " +
                             "Defaults to %(default)s.")
    parser.add_argument("--idfile", dest="idfile", type=str, default=None,
                        help="Read ID to start counting from from a file.")
    parser.add_argument("--saveid", dest="saveid", type=str, default=None,
                        help="Save last ID after execution to a file.")
    parser.add_argument("--positive-id", dest="positiveId", action="store_true",
                        help=argparse.SUPPRESS) # can cause problems when used inappropriately
    # output file options
    parser.add_argument("-o", "--output", dest="outputFile", metavar="OUTPUT",
                        help="Set destination .osm file name and location.")
    parser.add_argument("-f", "--force", dest="forceOverwrite", action="store_true",
                        help="Force overwrite of output file.")
    parser.add_argument("--no-upload-false", dest="noUploadFalse", action="store_true",
                        help="Omit upload=false from the completed file to suppress " +
                             "JOSM warnings when uploading.")
    parser.add_argument("--never-download", dest="neverDownload", action="store_true",
                        help="Prevent JOSM from downloading more data to this file.")
    parser.add_argument("--never-upload", dest="neverUpload", action="store_true",
                        help="Completely disables all upload commands for this file " +
                             "in JOSM, rather than merely showing a warning before " +
                             "uploading.")
    parser.add_argument("--locked", dest="locked", action="store_true",
                        help="Prevent any changes to this file in JOSM, " +
                             "such as editing or downloading, and also prevents uploads. " +
                             "Implies upload=\"never\" and download=\"never\".")
    parser.add_argument("--add-version", dest="addVersion", action="store_true",
                        help=argparse.SUPPRESS) # can cause problems when used inappropriately
    parser.add_argument("--add-timestamp", dest="addTimestamp", action="store_true",
                        help=argparse.SUPPRESS) # can cause problems when used inappropriately
    # required source file
    parser.add_argument("source", metavar="DATASOURCE",
                        help="DATASOURCE can be a file path or a org PostgreSQL connection " +
                             "string such as: \"PG:dbname=pdx_bldgs user=emma host=localhost\" " +
                             "(including the quotes)")
    params = parser.parse_args()
    
    if params.outputFile:
        params.outputFile = os.path.realpath(params.outputFile)

    # check consistency of parameters
    if params.source.startswith('PG:'):
        if not params.outputFile:
            parser.error("ERROR: An output file must be explicitly specified " +
                         "when using a database source")
        if not params.sqlQuery:
            parser.error("ERROR: You must specify a query with --sql when using a database source")
    else:
        if not params.outputFile:
            (base, ext) = os.path.splitext(os.path.basename(params.source))
            params.outputFile = os.path.join(os.getcwd(), base + ".osm.pbf")
        if params.sqlQuery:
            logging.warning("WARNING: You specified a query with --sql " +
                            "but you are not using a database source")

    if not params.forceOverwrite and os.path.exists(params.outputFile):
        parser.error("ERROR: output file '%s' exists" % (params.outputFile))
    
    return params


def load_translation_object(translation_module):
    import_translation_module = None
    translation_object = None

    if translation_module:
        # add dirs to path if necessary
        (root, ext) = os.path.splitext(translation_module)
        if os.path.exists(translation_module) and ext == '.py':
            # user supplied translation file directly
            sys.path.insert(0, os.path.dirname(root))
        else:
            # first check translations in the subdir translations of cwd
            sys.path.insert(0, os.path.join(os.getcwd(), "translations"))
            # then check subdir of script dir
            sys.path.insert(1, os.path.join(os.path.dirname(__file__), "translations"))
            # (the cwd will also be checked implicityly)

        # strip .py if present, as import wants just the module name
        if ext == '.py':
            translation_module = os.path.basename(root)

        imported_module = None
        try:
            imported_module = __import__(translation_module)
        except ImportError as e:
            logging.error("Could not load translation method '%s'. Translation "
                          "script must be in your current directory, or in the "
                          "translations/ subdirectory of your current or ogr2osm.py "
                          "directory. The following directories have been considered: %s"
                          % (translation_module, str(sys.path)))
        except SyntaxError as e:
            logging.error("Syntax error in '%s'. Translation script is malformed:\n%s"
                          % (translation_module, e))
    
        for class_name in [ d for d in dir(imported_module) \
                                    if d != 'TranslationBase' and not d.startswith('__') ]:
            translation_class = getattr(imported_module, class_name)

            if inspect.isclass(translation_class) and \
               issubclass(translation_class, TranslationBase):
                logging.info('Found valid translation class %s' % class_name)
                setattr(sys.modules[__name__], class_name, translation_class)
                translation_object = translation_class()
                break

    if not translation_object:
        logging.info('Using default translations')
        translation_object = TranslationBase()
    
    return translation_object


def main():
    params = parse_commandline()

    translation_object = load_translation_object(params.translationmodule)

    OsmId.set_id(params.id, params.positiveId)
    if params.idfile:
        OsmId.load_id(params.idfile)

    logging.info("Preparing to convert '%s' to '%s'." % (params.source, params.outputFile))

    osmdata = OsmData(translation_object, params.significantDigits, params.roundingDigits, \
                      params.maxNodesPerWay)
    # create datasource and process data
    datasource = OgrDatasource(translation_object, params.sourcePROJ4, params.sourceEPSG)
    datasource.open_datasource(params.source, not params.noMemoryCopy)
    datasource.set_query(params.sqlQuery)
    osmdata.process(datasource)
    #create datawriter and write OSM data
    #datawriter = OsmDataWriter(params.outputFile, params.neverUpload, params.noUploadFalse, \
    #                           params.neverDownload, params.locked, params.addVersion, \
    #                           params.addTimestamp)
    datawriter = PbfDataWriter(params.outputFile)
    osmdata.output(datawriter)

    if params.saveid:
        OsmId.save_id(params.saveid)



if __name__ == '__main__':
    main()

