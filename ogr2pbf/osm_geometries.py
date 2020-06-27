# -*- coding: utf-8 -*-

import logging
from lxml import etree

class OsmId:
    element_id_counter = 0
    element_id_counter_incr = -1

    @staticmethod
    def set_id(start_id, is_positive = False):
        OsmId.element_id_counter = start_id
        if is_positive:
            OsmId.element_id_counter_incr = 1


    @staticmethod
    def load_id(filename):
        with open(filename, 'r') as ff:
            OsmId.element_id_counter = int(ff.readline(20))
        logging.info("Starting counter value '%d' read from file '%s'." % \
                     (OsmId.element_id_counter, filename))


    @staticmethod
    def save_id(filename):
        with open(filename, 'w') as ff:
            ff.write(str(OsmId.element_id_counter))
        logging.info("Wrote elementIdCounter '%d' to file '%s'" % \
                     (OsmId.element_id_counter, filename))



class OsmGeometry:
    def __init__(self):
        self.id = self.__get_new_id()
        self.tags = { }
        self.__parents = set()
    
    
    def __get_new_id(self):
        OsmId.element_id_counter += OsmId.element_id_counter_incr
        return OsmId.element_id_counter
    
    
    def get_parents(self):
        return self.__parents
    
    
    def add_tags(self, tags):
        self.tags.update(tags)
    
    
    def replacejwithi(self, i, j):
        pass
    
    
    def to_xml(self, attributes = { }):
        pass
    
    
    def addparent(self, parent):
        self.__parents.add(parent)


    def removeparent(self, parent):
        self.__parents.discard(parent)



class OsmPoint(OsmGeometry):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
    
    
    def to_xml(self, attributes):
        xmlattrs = { 'visible':'true', \
                     'id':str(self.id), \
                     'lat':str(self.y),
                     'lon':str(self.x) }
        xmlattrs.update(attributes)

        xmlobject = etree.Element('node', xmlattrs)

        for (key, value) in self.tags.items():
            tag = etree.Element('tag', { 'k':key, 'v':value })
            xmlobject.append(tag)
        
        return etree.tostring(xmlobject, encoding='unicode')



class OsmWay(OsmGeometry):
    def __init__(self):
        super().__init__()
        self.points = []


    def replacejwithi(self, i, j):
        self.points = [ i if x == j else x for x in self.points ]
        j.removeparent(self)
        i.addparent(self)


    def to_xml(self, attributes):
        xmlattrs = { 'visible':'true', 'id':str(self.id) }
        xmlattrs.update(attributes)

        xmlobject = etree.Element('way', xmlattrs)

        for node in self.points:
            nd = etree.Element('nd', { 'ref':str(node.id) })
            xmlobject.append(nd)
        for (key, value) in self.tags.items():
            tag = etree.Element('tag', { 'k':key, 'v':value })
            xmlobject.append(tag)

        return etree.tostring(xmlobject, encoding='unicode')



class OsmRelation(OsmGeometry):
    def __init__(self):
        super().__init__()
        self.members = []


    def replacejwithi(self, i, j):
        self.members = [ (i, x[1]) if x[0] == j else x for x in self.members ]
        j.removeparent(self)
        i.addparent(self)


    def to_xml(self, attributes):
        xmlattrs = { 'visible':'true', 'id':str(self.id) }
        xmlattrs.update(attributes)

        xmlobject = etree.Element('relation', xmlattrs)

        for (member, role) in self.members:
            member = etree.Element('member', { 'type':'way', 'ref':str(member.id), 'role':role })
            xmlobject.append(member)

        tag = etree.Element('tag', { 'k':'type', 'v':'multipolygon' })
        xmlobject.append(tag)
        for (key, value) in self.tags.items():
            tag = etree.Element('tag', { 'k':key, 'v':value })
            xmlobject.append(tag)

        return etree.tostring(xmlobject, encoding='unicode')

