#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   un.py
@Time    :   2020/06/22 14:15:57
@Author  :   Frank Lee 
@Version :   1.0
@Contact :   lim@esrichina.com.cn
'''

# 创建utility network
import arcpy

#设置局部变量
fgdb = "E:/"
service_territory = ""

dataset = "SYSTEM"
network_name = "ElectricNetwork"
arcpy.pt.StageUtilityNetwork(fgdb,service_territory,dataset,network_name)
# 创建域网络
arcpy.AddDomainNetwork_un("ElectricNetwork","Electric","HIERARCHICAL","SOURCE","alias")
# 添加子类型
arcpy.SetSubtypeField_management("infeatures","field")
stypeDict = {"0":"Unknown","1":"变压器"，"2":""}
for code in stypeDict：
    arcpy.AddSubtype_management("infeature",code,stypeDict[code])
arcpy.SetDefaultSubtype_management("infeature",4)