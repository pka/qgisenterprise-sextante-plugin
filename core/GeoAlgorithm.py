# -*- coding: utf-8 -*-

"""
***************************************************************************
    GeoAlgorithmExecutionException.py
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
import traceback
import copy
from sextante.outputs.Output import Output
from sextante.parameters.Parameter import Parameter
from sextante.core.QGisLayers import QGisLayers
from sextante.parameters.ParameterRaster import ParameterRaster
from sextante.parameters.ParameterVector import ParameterVector
from PyQt4 import QtGui
from PyQt4.QtCore import *
from qgis.core import *
from sextante.core.SextanteUtils import SextanteUtils
from sextante.parameters.ParameterMultipleInput import ParameterMultipleInput
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from sextante.core.SextanteLog import SextanteLog
from sextante.outputs.OutputVector import OutputVector
from sextante.outputs.OutputRaster import OutputRaster
from sextante.outputs.OutputTable import OutputTable
from sextante.outputs.OutputHTML import OutputHTML
from sextante.core.SextanteConfig import SextanteConfig
from sextante.gdal.GdalUtils import GdalUtils

class GeoAlgorithm:

    def __init__(self):
        #parameters needed by the algorithm
        self.parameters = list()
        #outputs generated by the algorithm
        self.outputs = list()
        #name and group for normal toolbox display
        self.name = ""
        self.group = ""
        #the crs taken from input layers (if possible), and used when loading output layers
        self.crs = None
        #change any of the following if your algorithm should not appear in the toolbox or modeler
        self.showInToolbox = True
        self.showInModeler = True
        self.canRunInBatchMode = True
        #to be set by the provider when it loads the algorithm
        self.provider = None

        self.defineCharacteristics()

    def getCopy(self):
        newone = copy.copy(self)
        newone.parameters = copy.deepcopy(self.parameters)
        newone.outputs = copy.deepcopy(self.outputs)
        return newone

    #methods to overwrite when creating a custom geoalgorithm
    #=========================================================
    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/../images/alg.png")

    @staticmethod
    def getDefaultIcon():
        return QtGui.QIcon(os.path.dirname(__file__) + "/../images/alg.png")

    def helpFile(self):
        '''Returns the path to the help file with the description of this algorithm.
        It should be an HTML file. Returns None if there is no help file available'''
        return None

    def processAlgorithm(self):
        '''Here goes the algorithm itself
        There is no return value from this method.
        A GeoAlgorithmExecutionException should be raised in case something goes wrong.
        '''
        pass

    def defineCharacteristics(self):
        '''here is where the parameters and outputs should be defined'''
        pass

    def getCustomParametersDialog(self):
        '''if the algorithm has a custom parameters dialog, it should be returned
        here, ready to be executed'''
        return None

    def getCustomModelerParametersDialog(self, modelAlg, algIndex = None):
        '''if the algorithm has a custom parameters dialog when called from the modeler,
        it should be returned here, ready to be executed'''
        return None

    def getParameterDescriptions(self):
        '''Returns a dict with param names as keys and detailed descriptions of each param
        as value. These descriptions are used as tool tips in the parameters dialog.
        If a description does not exist, the parameter's human-readable name is used'''
        descs = {}
        return descs

    def checkBeforeOpeningParametersDialog(self):
        '''If there is any check to perform before the parameters dialog is opened,
        it should be done here. This method returns an error message string if there
        is any problem (for instance, an external app not configured yet), or None
        if the parameters dialog can be opened.
        Note that this check should also be done in the processAlgorithm method,
        since algorithms can be called without opening the parameters dialog.'''
        return None

    def checkParameterValuesBeforeExecuting(self):
        '''If there is any check to do before launching the execution of the algorithm,
        it should be done here. If values are not correct, a message should be returned
        explaining the problem
        This check is called from the parameters dialog, and also when calling from the console'''
        return None
    #=========================================================


    def execute(self, progress):
        '''The method to use to call a SEXTANTE algorithm.
        Although the body of the algorithm is in processAlgorithm(),
        it should be called using this method, since it performs
        some additional operations.
        Raises a GeoAlgorithmExecutionException in case anything goes wrong.'''

        try:
            self.setOutputCRS()
            self.resolveTemporaryOutputs()
            self.checkOutputFileExtensions()
            self.runPreExecutionScript(progress)
            self.processAlgorithm(progress)
            self.convertUnsupportedFormats(progress)
            self.runPostExecutionScript(progress)
        except GeoAlgorithmExecutionException, gaee:
            SextanteLog.addToLog(SextanteLog.LOG_ERROR, gaee.msg)
            raise gaee
        except:
            #if something goes wrong and is not caught in the algorithm,
            #we catch it here and wrap it
            lines = ["Uncaught error while executing algorithm"]
            errstring = traceback.format_exc()
            newline = errstring.find("\n")
            if newline != -1:
                lines.append(errstring[:newline])
            else:
                lines.append(errstring)
            lines.append(errstring.replace("\n", "|"))
            SextanteLog.addToLog(SextanteLog.LOG_ERROR, lines)
            raise GeoAlgorithmExecutionException(errstring)


    def runPostExecutionScript(self, progress):
        scriptFile = SextanteConfig.getSetting(SextanteConfig.POST_EXECUTION_SCRIPT)
        self.runHookScript(scriptFile, progress);

    def runPreExecutionScript(self, progress):
        scriptFile = SextanteConfig.getSetting(SextanteConfig.PRE_EXECUTION_SCRIPT)
        self.runHookScript(scriptFile, progress);

    def runHookScript(self, filename, progress):
        if not os.path.exists(filename):
            return
        try:
            script = "import sextante\n"
            ns = {}
            ns['progress'] = progress
            ns['alg'] = self
            f = open(filename)
            lines = f.readlines()
            for line in lines:
                script+=line
            exec(script) in ns
        except: # a wrong script should not cause problems, so we swallow all exceptions
            pass

    def convertUnsupportedFormats(self, progress):
        i = 0
        progress.setText("Converting outputs")
        for out in self.outputs:
            if isinstance(out, OutputVector):
                if out.compatible is not None:
                    layer = QGisLayers.getObjectFromUri(out.compatible)
                    if layer is None: # for the case of memory layer, if the getCompatible method has been called
                        continue
                    provider = layer.dataProvider()
                    writer = out.getVectorWriter( provider.fields(), provider.geometryType(), layer.crs())
                    features = QGisLayers.features(layer)
                    for feature in features:
                        writer.addFeature(feature)
            elif isinstance(out, OutputRaster):
                if out.compatible is not None:
                    layer = QGisLayers.getObjectFromUri(out.compatible)
                    provider = layer.dataProvider()
                    writer = QgsRasterFileWriter(out.value)
                    format = self.getFormatShortNameFromFilename(out.value)
                    writer.setOutputFormat(format);
                    writer.writeRaster(layer.pipe(), layer.width(), layer.height(), layer.extent(), layer.crs())
            elif isinstance(out, OutputTable):
                if out.compatible is not None:
                    layer = QGisLayers.getObjectFromUri(out.compatible)
                    provider = layer.dataProvider()
                    writer = out.getTableWriter(provider.fields())
                    features = QGisLayers.features(layer)
                    for feature in features:
                        writer.addRecord(feature)
            progress.setPercentage(100 * i / float(len(self.outputs)))

    def getFormatShortNameFromFilename(self, filename):
        ext = filename[filename.rfind(".")+1:]
        supported = GdalUtils.getSupportedRasters()
        for name in supported.keys():
            exts = supported[name]
            if ext in exts:
                return name
        return "GTiff"

    def checkOutputFileExtensions(self):
        '''Checks if the values of outputs are correct and have one of the supported output extensions.
        If not, it adds the first one of the supported extensions, which is assumed to be the default one'''
        for out in self.outputs:
            if (not out.hidden) and out.value != None:
                if not os.path.isabs(out.value):
                    continue
                if isinstance(out, OutputRaster):
                    exts = QGisLayers.getSupportedOutputRasterLayerExtensions()
                elif isinstance(out, OutputVector):
                    exts = QGisLayers.getSupportedOutputVectorLayerExtensions()
                elif isinstance(out, OutputTable):
                    exts = QGisLayers.getSupportedOutputTableExtensions()
                elif isinstance(out, OutputHTML):
                    exts =["html", "htm"]
                else:
                    continue
                idx = out.value.rfind(".")
                if idx == -1:
                    out.value = out.value + "." + exts[0]
                else:
                    ext = out.value[idx + 1:]
                    if ext not in exts:
                        out.value = out.value + "." + exts[0]

    def resolveTemporaryOutputs(self):
        '''sets temporary outputs (output.value = None) with a temporary file instead'''
        for out in self.outputs:
            if (not out.hidden) and out.value == None:
                SextanteUtils.setTempOutput(out, self)

    def setOutputCRS(self):
        layers = QGisLayers.getAllLayers()
        for param in self.parameters:
            if isinstance(param, (ParameterRaster, ParameterVector, ParameterMultipleInput)):
                if param.value:
                    inputlayers = param.value.split(";")
                    for inputlayer in inputlayers:
                        for layer in layers:
                            if layer.source() == inputlayer:
                                self.crs = layer.crs()
                                return
        qgis = QGisLayers.iface
        self.crs = qgis.mapCanvas().mapRenderer().destinationCrs()

    def checkInputCRS(self):
        '''it checks that all input layers use the same CRS. If so, returns True. False otherwise'''
        crs = None;
        layers = QGisLayers.getAllLayers()
        for param in self.parameters:
            if isinstance(param, (ParameterRaster, ParameterVector, ParameterMultipleInput)):
                if param.value:
                    inputlayers = param.value.split(";")
                    for inputlayer in inputlayers:
                        for layer in layers:
                            if layer.source() == inputlayer:
                                if crs is None:
                                    crs = layer.crs()
                                else:
                                    if crs != layer.crs():
                                        return False
        return True

    def addOutput(self, output):
        #TODO: check that name does not exist
        if isinstance(output, Output):
            self.outputs.append(output)

    def addParameter(self, param):
        #TODO: check that name does not exist
        if isinstance(param, Parameter):
            self.parameters.append(param)

    def setParameterValue(self, paramName, value):
        for param in self.parameters:
            if param.name == paramName:
                return param.setValue(value)

    def setOutputValue(self, outputName, value):
        for out in self.outputs:
            if out.name == outputName:
                out.value = value

    def getVisibleOutputsCount(self):
        '''returns the number of non-hidden outputs'''
        i = 0;
        for out in self.outputs:
            if not out.hidden:
                i+=1
        return i;

    def getVisibleParametersCount(self):
        '''returns the number of non-hidden parameters'''
        i = 0;
        for param in self.parameters:
            if not param.hidden:
                i+=1
        return i;

    def getOutputValuesAsDictionary(self):
        d = {}
        for out in self.outputs:
            d[out.name] = out.value
        return d


    def __str__(self):
        s = "ALGORITHM: " + self.name + "\n"
        for param in self.parameters:
            s+=("\t" + str(param) + "\n")
        for out in self.outputs:
            #if not out.hidden:
            s+=("\t" + str(out) + "\n")
        s+=("\n")
        return s


    def commandLineName(self):
        name = self.provider.getName().lower() + ":" + self.name.lower()
        validChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:"
        name = ''.join(c for c in name if c in validChars)
        return name
        

    def removeOutputFromName(self, name):
        for out in self.outputs:
            if out.name == name:
                self.outputs.remove(out)

    def getOutputFromName(self, name):
        for out in self.outputs:
            if out.name == name:
                return out

    def getParameterFromName(self, name):
        for param in self.parameters:
            if param.name == name:
                return param

    def getParameterValue(self, name):
        for param in self.parameters:
            if param.name == name:
                return param.value
        return None

    def getOutputValue(self, name):
        for out in self.outputs:
            if out.name == name:
                return out.value
        return None

    def getAsCommand(self):
        '''Returns the command that would run this same algorithm from the console.
        Should return null if the algorithm cannot be run from the console.'''
        s="sextante.runalg(\"" + self.commandLineName() + "\","
        for param in self.parameters:
            s+=param.getValueAsCommandLineParameter() + ","
        for out in self.outputs:
            if not out.hidden:
                s+=out.getValueAsCommandLineParameter() + ","
        s= s[:-1] + ")"
        return s


