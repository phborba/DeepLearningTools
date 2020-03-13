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

import os
from pathlib import Path
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterBoolean,
                       QgsProcessingException,
                       QgsProcessingParameterNumber
                       )
from DeepLearningTools.core.image_processing.image_utils import ImageUtils
import concurrent.futures


class CreateTrainingLabelsFromLayerAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    IMAGE_ATTRIBUTE = 'IMAGE_ATTRIBUTE'
    OUTPUT_LABEL_ATTRIBUTE_PATH = 'OUTPUT_LABEL_ATTRIBUTE_PATH'
    INPUT = 'INPUT'
    INPUT_POLYGONS = 'INPUT_POLYGONS'
    SELECTED = 'SELECTED'
    NUM_CPU = 'NUM_CPU'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTED,
                self.tr('Process only selected features')
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.IMAGE_ATTRIBUTE,
                self.tr('Image attribute'),
                None, 
                'INPUT',
                QgsProcessingParameterField.Any
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.OUTPUT_LABEL_ATTRIBUTE_PATH,
                self.tr('Output label attribute'),
                None, 
                'INPUT',
                QgsProcessingParameterField.Any
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_POLYGONS,
                self.tr('Input polygons'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.NUM_CPU,
                self.tr('Number of CPUs used in processing'),
                QgsProcessingParameterNumber.Integer,
                defaultValue=1,
                minValue=1,
                maxValue=os.cpu_count()
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        inputLyr = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        if inputLyr is None:
            raise QgsProcessingException(
                self.invalidSourceError(
                    parameters,
                    self.INPUT
                )
            )
        onlySelected = self.parameterAsBool(
            parameters,
            self.SELECTED,
            context
        )
        featCount = inputLyr.featureCount() if not onlySelected \
            else inputLyr.selectedFeatureCount()
        features = inputLyr.getFeatures() if not onlySelected \
            else inputLyr.getSelectedFeatures()
        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / featCount if featCount else 0

        image_attribute = self.parameterAsFields(
            parameters,
            self.IMAGE_ATTRIBUTE,
            context
        )[0]

        output_attribute = self.parameterAsFields(
            parameters,
            self.OUTPUT_LABEL_ATTRIBUTE_PATH,
            context
        )[0]
        image_utils = ImageUtils()
        inputPolygonsLyr = self.parameterAsVectorLayer(
            parameters,
            self.INPUT_POLYGONS,
            context
        )
        if inputPolygonsLyr is None:
            raise QgsProcessingException(
                self.invalidSourceError(
                    parameters,
                    self.INPUT_POLYGONS
                )
            )
        num_workers = self.parameterAsInt(
            parameters,
            self.NUM_CPU,
            context
        )
        def compute(feature):
            output_folder = os.path.dirname(
                    feature[output_attribute]
                )
            Path(output_folder).mkdir(
                parents=True,
                exist_ok=True
            )
            image_utils.create_image_label(
                feature[image_attribute],
                feature[output_attribute],
                inputPolygonsLyr
            )
        
        pool = concurrent.futures.ThreadPoolExecutor(num_workers)
        futures = []
        current_feat = 0
        for feat in features:
            if feedback.isCanceled():
                break
            futures.append(pool.submit(compute, feat))
        for x in concurrent.futures.as_completed(futures):
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current_feat * total))
            current_feat += 1
            # print(x.result())

        return {}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Create Training Labels From Vector Data'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Labelling'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CreateTrainingLabelsFromLayerAlgorithm()
