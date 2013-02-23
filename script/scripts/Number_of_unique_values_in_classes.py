# -*- coding: utf-8 -*-

"""
***************************************************************************
    Number_of_unique_values_in_classes.py
    ---------------------
    Date                 : November 2012
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
__date__ = 'November 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

#Definition of inputs and outputs
#==================================
##[Example scripts]=group
##input=vector
##class_field=field input
##value_field=field input
##output=output vector

#Algorithm body
#==================================
from qgis.core import *
from PyQt4.QtCore import *
from sextante.core.SextanteVectorWriter import SextanteVectorWriter

# "input" contains the location of the selected layer.
# We get the actual object, so we can get its bounds
layer = getobject(input)
provider = layer.dataProvider()
fields = provider.fields()
fields.append(QgsField("UNIQ_COUNT", QVariant.Int))
writer = SextanteVectorWriter(output, None, fields, provider.geometryType(), provider.crs() )

# Fields are defined by their names, but QGIS needs the index for the attributes map
class_field_index = layer.fieldNameIndex(class_field)
value_field_index = layer.fieldNameIndex(value_field)

inFeat = QgsFeature()
outFeat = QgsFeature()
inGeom = QgsGeometry()
nElement = 0
classes = {}

#Iterate over input layer to count unique values in each class

feats = getfeatures(layer)
nFeat = len(feates)
for inFeat in feats:
    progress.setPercentage(int((100 * nElement)/nFeat))
    nElement += 1
    attrs = inFeat.attributes()
    clazz = attrs[class_field_index].toString()
    value = attrs[value_field_index].toString()
    if clazz not in classes:
        classes[clazz] = []
    if value not in classes[clazz]:
        classes[clazz].append(value)

# Create output vector layer with additional attribute
feats = getfeatures(layer)
nElement = 0
for inFeat in feats: 
    progress.setPercentage(int((100 * nElement)/nFeat))
    nElement += 1
    inGeom = inFeat.geometry()
    outFeat.setGeometry(inGeom)
    attrs = inFeat.attributes()
    clazz = attrs[class_field_index].toString()
    attrs.append(QVariant(len(classes[clazz])))
    outFeat.setAttributes(attrs)    
    writer.addFeature(outFeat)

del writer
