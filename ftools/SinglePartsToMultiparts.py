# -*- coding: utf-8 -*-

"""
***************************************************************************
    SinglePartsToMultiparts.py
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

import os.path

from PyQt4 import QtGui
from PyQt4.QtCore import *

from qgis.core import *

from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from sextante.core.QGisLayers import QGisLayers

from sextante.parameters.ParameterVector import ParameterVector
from sextante.parameters.ParameterTableField import ParameterTableField

from sextante.outputs.OutputVector import OutputVector

class SinglePartsToMultiparts(GeoAlgorithm):

    INPUT = "INPUT"
    FIELD = "FIELD"
    OUTPUT = "OUTPUT"

    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/icons/single_to_multi.png")

    def defineCharacteristics(self):
        self.name = "Singleparts to multipart"
        self.group = "Geometry tools"

        self.addParameter(ParameterVector(self.INPUT, "Input layer"))
        self.addParameter(ParameterTableField(self.FIELD, "Unique ID field", self.INPUT))

        self.addOutput(OutputVector(self.OUTPUT, "Output layer"))

    def processAlgorithm(self, progress):
        layer = QGisLayers.getObjectFromUri(self.getParameterValue(self.INPUT))
        output = self.getOutputValue(self.OUTPUT)
        fieldName = self.getParameterValue(self.FIELD)

        provider = layer.dataProvider()
        allAttrs = layer.pendingAllAttributesList()
        layer.select(allAttrs)
        geomType = self.singleToMultiGeom(provider.geometryType())

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(layer.pendingFields(),
                     geomType, provider.crs())

        inFeat = QgsFeature()
        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        outGeom = QgsGeometry()

        index = layer.fieldNameIndex(fieldName)
        unique = layer.uniqueValues(index)

        current = 0
        total = 100.0 / float(provider.featureCount() * len(unique))

        if not len(unique) == layer.featureCount():
            for i in unique:
                provider.rewind()
                multi_feature= []
                first = True
                layer.select(allAttrs)
                while layer.nextFeature(inFeat):
                    atMap = inFeat.attributeMap()
                    idVar = atMap[index]
                    if idVar.toString().trimmed() == i.toString().trimmed():
                        if first:
                            attrs = atMap
                            print attrs
                            first = False
                        inGeom = QgsGeometry(inFeat.geometry())
                        vType = inGeom.type()
                        feature_list = self.extractAsMulti(inGeom)
                        multi_feature.extend(feature_list)

                    current += 1
                    progress.setPercentage(int(current * total))

                outFeat.setAttributeMap(attrs)
                outGeom = QgsGeometry(self.convertGeometry(multi_feature, vType))
                outFeat.setGeometry(outGeom)
                writer.addFeature(outFeat)

            del writer
        else:
            raise GeoAlgorithmExecutionException("Invalid unique ID field")

    def singleToMultiGeom(self, wkbType):
      try:
          if wkbType in (QGis.WKBPoint, QGis.WKBMultiPoint,
                          QGis.WKBPoint25D, QGis.WKBMultiPoint25D):
              return QGis.WKBMultiPoint
          elif wkbType in (QGis.WKBLineString, QGis.WKBMultiLineString,
                            QGis.WKBMultiLineString25D, QGis.WKBLineString25D):
              return QGis.WKBMultiLineString
          elif wkbType in (QGis.WKBPolygon, QGis.WKBMultiPolygon,
                            QGis.WKBMultiPolygon25D, QGis.WKBPolygon25D):
              return QGis.WKBMultiPolygon
          else:
              return QGis.WKBUnknown
      except Exception, err:
          print unicode(err)

    def extractAsMulti(self, geom):
      if geom.type() == QGis.Point:
          if geom.isMultipart():
              return geom.asMultiPoint()
          else:
              return [geom.asPoint()]
      elif geom.type() == QGis.Line:
          if geom.isMultipart():
              return geom.asMultiPolyline()
          else:
              return [geom.asPolyline()]
      else:
          if geom.isMultipart():
              return geom.asMultiPolygon()
          else:
              return [geom.asPolygon()]

    def convertGeometry(self, geom_list, vType):
      if vType == QGis.Point:
          return QgsGeometry().fromMultiPoint(geom_list)
      elif vType == QGis.Line:
          return QgsGeometry().fromMultiPolyline(geom_list)
      else:
          return QgsGeometry().fromMultiPolygon(geom_list)
