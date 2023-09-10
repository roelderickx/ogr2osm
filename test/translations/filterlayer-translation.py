# -*- coding: utf-8 -*-

'''
Copyright (c) 2012-2021 Roel Derickx, Paul Norman <penorman@mac.com>,
Sebastiaan Couwenberg <sebastic@xs4all.nl>, The University of Vermont
<andrew.guertin@uvm.edu>, github contributors

Released under the MIT license, as given in the file LICENSE, which must
accompany any distribution of this code.
'''

import ogr2osm, logging

class FilterLayerTranslation(ogr2osm.TranslationBase):
    def __init__(self):
        self.logger = logging.getLogger('ogr2osm')


    def filter_layer(self, layer):
        # suppress all layers
        return None
