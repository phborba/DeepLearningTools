# -*- coding: utf-8 -*-

"""
/***************************************************************************
 DeepLearningTools
                                 A QGIS plugin
 QGIS plugin to aid training Deep Learning Models
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-03-12
        copyright            : (C) 2020 by Philipe Borba
        email                : philipeborba@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Philipe Borba'
__date__ = '2020-03-12'
__copyright__ = '(C) 2020 by Philipe Borba'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import inspect

from qgis.core import QgsProcessingAlgorithm, QgsApplication
from .deep_learning_tools_provider import DeepLearningToolsProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

try:
    import ptvsd
    ptvsd.enable_attach(address = ('localhost', 5677))
except Exception as e:
    pass

class DeepLearningTools(object):

    def __init__(self):
        self.provider = None

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = DeepLearningToolsProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
