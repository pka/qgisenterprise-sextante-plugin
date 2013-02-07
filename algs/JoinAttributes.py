# -*- coding: utf-8 -*-

"""
***************************************************************************
    JoinAttributes.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.outputs.OutputVector import OutputVector
from sextante.parameters.ParameterVector import ParameterVector
from sextante.parameters.ParameterTableField import ParameterTableField
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sextante.core.QGisLayers import QGisLayers


class JoinAttributes(GeoAlgorithm):

    OUTPUT_LAYER = "OUTPUT_LAYER"
    INPUT_LAYER = "INPUT_LAYER"
    INPUT_LAYER_2 = "INPUT_LAYER_2"
    TABLE_FIELD = "TABLE_FIELD"
    TABLE_FIELD_2 = "TABLE_FIELD_2"

    def defineCharacteristics(self):
        self.name = "Join attributes table"
        self.group = "Vector general tools"
        self.addParameter(ParameterVector(self.INPUT_LAYER, "Input layer", ParameterVector.VECTOR_TYPE_ANY, False))
        self.addParameter(ParameterVector(self.INPUT_LAYER_2, "Input layer 2", ParameterVector.VECTOR_TYPE_ANY, False))
        self.addParameter(ParameterTableField(self.TABLE_FIELD, "Table field", self.INPUT_LAYER))
        self.addParameter(ParameterTableField(self.TABLE_FIELD_2, "Table field 2", self.INPUT_LAYER_2))
        self.addOutput(OutputVector(self.OUTPUT_LAYER, "Output layer"))

    def processAlgorithm(self, progress):
        input = self.getParameterValue(self.INPUT_LAYER)
        input2 = self.getParameterValue(self.INPUT_LAYER_2)
        output = self.getOutputFromName(self.OUTPUT_LAYER)
        field = self.getParameterValue(self.TABLE_FIELD)
        field2 = self.getParameterValue(self.TABLE_FIELD_2)

        # Layer 1
        layer = QGisLayers.getObjectFromUri(input)
        provider = layer.dataProvider()
        join_field1_index = layer.fieldNameIndex(field)
        # Layer 2
        layer2 = QGisLayers.getObjectFromUri(input2)
        provider2 = layer2.dataProvider()
        fields2 = provider2.fields()
        join_field2_index = layer2.fieldNameIndex(field2)

        # Output
        outFields = input.fields()
        for f in fields2:
            outFields.append(f)

        writer = output.getVectorWriter(outFields, provider.geometryType(), provider.crs())

        inFeat = QgsFeature()
        inFeat2 = QgsFeature()
        outFeat = QgsFeature()

        # Create output vector layer with additional attribute
        features = QGisLayers.features(layer);
        for inFeat in features:
            inGeom = inFeat.geometry()
            atMap = inFeat.attributes()
            join_value1 = atMap[join_field1_index].toString()
            while provider2.nextFeature(inFeat2):
                ## Maybe it should cache this entries...
                atMap2 = inFeat2.attributeMap()
                join_value2 = atMap2[join_field2_index].toString()
                if join_value1 == join_value2:
                    # create the new feature
                    outFeat.setGeometry(inGeom)
                    atMap.extend(atMap2)
                    break;
            outFeat.setAttributes(atMap)
            writer.addFeature(outFeat)

        del writer
