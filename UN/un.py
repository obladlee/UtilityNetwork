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

stypeDict = {"0":"Unknown","1":"变压器","2":""}
for code in stypeDict:
    arcpy.AddSubtype_management("infeature",code,stypeDict[code])
arcpy.SetDefaultSubtype_management("infeature",4)

stypeDict1 = {"0":"Unknown","1":"传输线"}

for code in stypeDict1:
    arcpy.addSubtype_management("infeature",code,stypeDict1[code])
arcpy.SetDefaultSubtype_management("infeature",)

#创建属性域,添加域值，分配给字段
#创建变压器属性域
arcpy.CreateDomain_management("gdb",domain_name=,domain_description=,field_type=short,domain_type=coded,)
domDict = {
    "1":"y=高压","2":"低压","3":"中压"
}
for code in domDict:
    arcpy.AddCodedValueToDomain_management(gdb,domName,code,domDict[code])
arcpy.AssignDomainToField_management(infeatures,inField,domname)
#创建传输线属性域

# 添加终端
arcpy.AddTerminalConfiguration_un(network_name,"config1","DIRECTIONAL",'A true;B true;C false','Top A-B;Bottom A-C','Bottom)
arcpy.SetTerminalConfiguration_un(network_name,"Electric","ElectricDevice","变压器","高压","config1")

# 添加网络分组
arcpy.AddNetworkCategory_un(network_name, 'Protective')
arcpy.SetNetworkCategory_un(network_name, "Electric", "ElectricDevice", "变压器", "高压变压器","Protective")

# 创建关联关系
arcpy.SetAssociationRole_un(network_name, "Electric", "ElectricDevice", "变压器","高压变压器", "none", "RESTRICTED")
arcpy.SetAssociationRole_un(network_name, "Electric", "ElectricDevice", "变压器","中压变压器", "none", "RESTRICTED")
arcpy.SetAssociationRole_un(network_name, "Electric", "ElectricDevice", "传输线","高压传输线", "none", "RESTRICTED")
arcpy.AddRule_un(network_name, "JUNCTION_EDGE_CONNECTIVITY", "ElectricDevice", "变压器", "高压变压器", "ElectricLine", "传输线","高压传输线")
arcpy.AddRule_un(network_name, "JUNCTION_EDGE_CONNECTIVITY", "ElectricDevice", "传输线", "高压传输线", "ElectricLine", "变压器","中压变压器")
# 设置线联通策略
arcpy.SetEdgeConnectivity_un(network_name, "Electric","ElectricLine", "传输线","高压传输线", "AnyVertex")
# 添加网络属性
arcpy.AddNetworkAttribute_un("Utility Network", "Device Status", "SHORT", "INLINE", "NOT_APPORTIONABLE", "",  "ElectricDistributionDeviceStatus", "NOT_OVERRIDABLE")
# 添加层和
arcpy.AddTier_un("Utility Network", "GasDistribution", "Distribution System",1, "MESH", "Distribution", "System")