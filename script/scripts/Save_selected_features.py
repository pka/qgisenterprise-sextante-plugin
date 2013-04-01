# -*- coding: utf-8 -*-

"""
***************************************************************************
    Save_selected_features.py
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

__author__ = 'Victor Olaya'
__date__ = 'November 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sextante.core.SextanteVectorWriter import SextanteVectorWriter

#Here we define the input and outputs
#====================================
##[Example scripts]=group
##input=vector
##output=output vector

#And here is the body of the algorithm
#=======================================

#input layers values are always a string with its location.
#That string can be converted into a QGIS object (a QgsVectorLayer in this case))
#using the sextante.getobject() method
vectorLayer = sextante.getobject(input)

#And now we can process

#First we create the output layer.
#To do so, we create a SextanteVectorWriter, that we can later use to add features.
provider = vectorLayer.dataProvider()
writer = SextanteVectorWriter(output, None, provider.fields(), provider.geometryType(), vectorLayer.crs())

#Now we take the selected features and add them to the output layer
selection = vectorLayer.selectedFeatures()
for feat in selection:
    writer.addFeature(feat)
del writer

#There is nothing more to do here. We do not have to open the layer that we have created.
#SEXTANTE will take care of that, or will handle it if this algorithm is executed within
#a complex model