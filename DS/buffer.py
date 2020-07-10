#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   buffer.py
@Time    :   2020/07/07 16:48:11
@Author  :   Frank Lee 
@Version :   1.0
@Contact :   lim@esrichina.com.cn
'''

import arcpy
# arcpy.env.workspace = "D:\something\Data.gdb"

# 脚本工具参数
InputFeature = arcpy.GetParameterAsText(0)
SingleRingWidth = arcpy.GetParameterAsText(1)
OutputFeature = arcpy.GetParameterAsText(2)

# 预设参数

distances = []
level = 9
bufferUnit = "meters"
NewField = "Percent"

# 构建缓冲距离列表
for i in range(level):
    distances.append(SingleRingWidth*(i+1))
    i = i+1

arcpy.AddMessage('step1 distances list complete!')

arcpy.MultipleRingBuffer_analysis(InputFeature,OutputFeature,distances,bufferUnit,"","ALL","outside_only")
arcpy.AddMessage('step2 success to execute multi ring buffer')

arcpy.AddField_management(OutputFeature,NewField,"double")
arcpy.AddMessage('step3 success to add transparancy percent field.')

arcpy.CalculateField_management(OutputFeature,NewField,"!OBJECT!*10","python","")

InputFeatureCount = int(arcpy.GetCount_management(OutputFeature).getoutput(0))
if InputFeatureCount == 0:
    arcpy.AddWarning("{0} has no features.".format(OutputFeature))
else:
    arcpy.AddMessage("step4 success to calculate transparency percent field!")
