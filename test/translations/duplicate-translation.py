# -*- coding: utf-8 -*-

'''
Copyright (c) 2012-2021 Roel Derickx, Paul Norman <penorman@mac.com>,
Sebastiaan Couwenberg <sebastic@xs4all.nl>, The University of Vermont
<andrew.guertin@uvm.edu>, github contributors

Released under the MIT license, as given in the file LICENSE, which must
accompany any distribution of this code.
'''

import ogr2osm, logging

class DuplicateTranslation(ogr2osm.TranslationBase):
    def __init__(self):
        super().__init__()
        self.node_counter = 0


    def merge_tags(self, geometry_type, tags_existing_geometry, tags_new_geometry):
        if geometry_type == 'node':
            self.node_counter += 1
        if geometry_type != 'node' or self.node_counter <= 10:
            self.logger.debug('Merging tags for duplicate %s' % geometry_type)
        return super().merge_tags(geometry_type, tags_existing_geometry, tags_new_geometry)
