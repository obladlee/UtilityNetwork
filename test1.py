from sklearn.ensemble import RandomForestClassifier
import numpy as NUM
import arcpy as ARCPY
import arcpy.da as DA
import pandas as PD
import seaborn as SEA
import matplotlib.pyplot as PLOT
import arcgisscripting as ARC
import SSUtilities as UTILS
import os as OS
ARCPY.env.workspace = 'E:\X-EsriTraining\AI_ARCGISPRO\SeagrassPrediction\SeagrassPrediction.gdb'
inputFC = r'USA_Train'
globalFC = r'EMU_Global_90m_Filled'
predictVars = ['DISSO2', 'NITRATE', 'PHOSPHATE', 'SALINITY', 'SILICATE', 'SRTM30', 'TEMP']
classVar = ['PRESENT']
allVars = predictVars + classVar
trainFC = DA.FeatureClassToNumPyArray(inputFC, ["SHAPE@XY"] + allVars)
spatRef = ARCPY.Describe(inputFC).spatialReference
data = PD.DataFrame(trainFC, columns = allVars)
corr = data.astype('float64').corr()
ax = SEA.heatmap(corr, cmap=SEA.diverging_palette(220, 10, as_cmap=True),
square=True, annot = True, linecolor = 'k', linewidths = 1)
PLOT.show()

fracNum = 0.1
train_set = data.sample(frac=fracNum)
test_set = data.drop(train_set.index)
indicator, _ = PD.factorize(train_set[classVar[0]])
print('Training Data Size = ' + str(train_set.shape[0]))
print('Test Data Size = ' + str(test_set.shape[0]))

rfco = RandomForestClassifier(n_estimators=500, oob_score=True)
rfco.fit(train_set[predictVars], indicator)
seagrassPred = rfco.predict(test_set[predictVars])
test_seagrass = test_set[classVar].as_matrix()
modpython: 1: FutureWarning: Method .as_matrix will be removed in a future version. Use .values instead.
test_seagrass = test_seagrass.flatten()
error = NUM.sum(NUM.abs(test_seagrass - seagrassPred))/len(seagrassPred) * 100
print('Accuracy = ' + str(100 - NUM.abs(error)) + '%')
print('Locations with Seagrass = ' +
      str(len(NUM.where(test_seagrass == 1)[0])))
print('Predicted Locations with Seagrass = ' +
      str(len(NUM.where(seagrassPred == 1)[0])))
indicatorUSA, _ = PD.factorize(data[classVar[0]])
rfco = RandomForestClassifier(n_estimators=500)
rfco.fit(data[predictVars], indicatorUSA)
globalData = DA.FeatureClassToNumPyArray(globalFC, ["SHAPE@XY"] + predictVars)
spatRefGlobal = ARCPY.Describe(globalFC).spatialReference

globalTrain = PD.DataFrame(globalData, columns=predictVars)
seagrassPredGlobal = rfco.predict(globalTrain)
nameFC = 'GlobalPrediction'
outputDir = r'E:\X-EsriTraining\AI_ARCGISPRO\SeagrassPrediction\SeagrassPrediction.gdb'
grassExists = globalData[["SHAPE@XY"]
                         ][globalTrain.index[NUM.where(seagrassPredGlobal == 1)]]
ARCPY.da.NumPyArrayToFeatureClass(grassExists, OS.path.join(
    outputDir, nameFC), ['SHAPE@XY'], spatRefGlobal)
