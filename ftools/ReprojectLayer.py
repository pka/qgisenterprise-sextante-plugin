# -*- coding: utf-8 -*-

"""
***************************************************************************
    ReprojectLayer.py
    ---------------------
    Date                 : October 2012
    Copyright            : (C) 2012 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'October 2012'
__copyright__ = '(C) 2012, Alexander Bruy'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os.path

from PyQt4 import QtGui
from PyQt4.QtCore import *

from qgis.core import *

from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.QGisLayers import QGisLayers
from sextante.core.SextanteLog import SextanteLog

from sextante.parameters.ParameterVector import ParameterVector
from sextante.parameters.ParameterCrs import ParameterCrs

from sextante.outputs.OutputVector import OutputVector

class ReprojectLayer(GeoAlgorithm):

    INPUT = "INPUT"
    TARGET_CRS = "TARGET_CRS"
    OUTPUT = "OUTPUT"

    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/icons/reproject.png")

    def defineCharacteristics(self):
        self.name = "Reproject layer"
        self.group = "Data management tools"

        self.addParameter(ParameterVector(self.INPUT, "Input layer", ParameterVector.VECTOR_TYPE_ANY))
        self.addParameter(ParameterCrs(self.TARGET_CRS, "Target CRS", "4326"))

        self.addOutput(OutputVector(self.OUTPUT, "Reprojected layer"))

    def processAlgorithm(self, progress):
        layer = QGisLayers.getObjectFromUri(self.getParameterValue(self.INPUT))
        crsId = self.getParameterValue(self.TARGET_CRS)
        targetCrs = QgsCoordinateReferenceSystem(int(crsId))

        output = self.getOutputValue(self.OUTPUT)

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(layer.pendingFields(),
                     layer.wkbType(), targetCrs)

        layer.select(layer.pendingAllAttributesList())

        current = 0
        total = 100.0 / float(layer.featureCount())

        layerCrs = layer.crs()
        crsTransform = QgsCoordinateTransform(layerCrs, targetCrs)

        f = QgsFeature()
        outFeat = QgsFeature()
        while layer.nextFeature(f):
            geom = f.geometry()
            geom.transform(crsTransform)
            outFeat.setGeometry(geom)
            outFeat.setAttributeMap(f.attributeMap())
            writer.addFeature(outFeat)

            current += 1
            progress.setPercentage(int(current * total))

        del writer
