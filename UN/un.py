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

#创建属性域,添加域值，分配给字段
arcpy.CreateDomain_management("gdb",domain_name=,domain_description=,field_type=short,domain_type=coded,)
domDict = {
    "1":"y=高压","2":"低压","3":"中压"
}
for code in domDict:
    arcpy.AddCodedValueToDomain_management(gdb,domName,code,domDict[code])
arcpy.AssignDomainToField_management(infeatures,inField,domname)
# 添加终端
arcpy.AddTerminalConfiguration_un()
