import os.path

from PyQt4 import QtGui
from PyQt4.QtCore import *

from qgis.core import *

from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.QGisLayers import QGisLayers

from sextante.parameters.ParameterVector import ParameterVector

from sextante.outputs.OutputVector import OutputVector

from sextante.ftools import FToolsUtils as utils

class ExtractNodes(GeoAlgorithm):

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/icons/extract_nodes.png")

    def defineCharacteristics(self):
        self.name = "Extract nodes"
        self.group = "Geometry tools"

        self.addParameter(ParameterVector(self.INPUT, "Input layer", ParameterVector.VECTOR_TYPE_ANY))

        self.addOutput(OutputVector(self.OUTPUT, "Output layer"))

    def processAlgorithm(self, progress):
        settings = QSettings()
        encoding = settings.value("/UI/encoding", "System").toString()

        layer = QGisLayers.getObjectFromUri(self.getParameterValue(self.INPUT))
        output = self.getOutputValue(self.OUTPUT)

        provider = layer.dataProvider()
        layer.select(layer.pendingAllAttributesList())

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(layer.pendingFields(),
                     QGis.WKBPoint, provider.crs())

        inFeat = QgsFeature()
        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        outGeom = QgsGeometry()

        current = 0
        total = 100.0 / float(provider.featureCount())

        while layer.nextFeature(inFeat):
            inGeom = inFeat.geometry()
            atMap = inFeat.attributeMap()

            points = utils.extractPoints(inGeom)
            outFeat.setAttributeMap(atMap)

            for i in points:
                outFeat.setGeometry(outGeom.fromPoint(i))
                writer.addFeature(outFeat)

            current += 1
            progress.setPercentage(int(current * total))

        del writer
