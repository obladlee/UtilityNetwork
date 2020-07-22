#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   createun.py
@Time    :   2020/07/13 09:03:54
@Author  :   liming 
@Version :   1.0
@Contact :   lim@esrichina.com.cn
'''

# 创建utility network
import arcpy
import os

arcpy.env.preserveGlobalIds = True

#设置输入参数
fgdb = "E:/ArcGIS/pro_Projects/Eleun/Eleun.gdb"
service_territory = "E:/ArcGIS/pro_Projects/ele.gdb/Service_Area"
dataset = "SYSTEM"
un = "ElectricNetwork"
domainNet,domainNetAlias = "Electric",'电网'

# elebyq = "E:/ArcGIS/pro_Projects/Eleun/ele变压器"
# elecsx = "E:/ArcGIS/pro_Projects/Eleun/ele传输线"

arcpy.env.workspace = os.path.join(fgdb, dataset)
# 创建un和结构网络
arcpy.pt.StageUtilityNetwork(fgdb,service_territory,dataset,un) 
arcpy.AddDomainNetwork_un(un,domainNet,"PARTITIONED","SOURCE",domainNetAlias)

    
# 子类由un自动创建，只需要增加内容f
# Unknown子类型也由un自动创建
domainNetSubtypes = {"ElectricDevice":{"1":"变压器"},"ElectricLine":{"1":"传输线"}}
for in_table, subtypes in domainNetSubtypes.items():  # items()是一个python字典的小技巧，同时返回key和value
    for code, name in subtypes.items():
        arcpy.AddSubtype_management(in_table,code,name)
    arcpy.SetDefaultSubtype_management(in_table, 1)  # 如果默认子类不是1，这里还需要额外的输入参数

#创建属性域,添加域值,分配给字段
#创建变压器属性域
codedDomains = {'电压': ('电压类型', ('Unknown','高压','低压'))}
assignDomainField = [('ElectricDevice', 'Asset type', '电压', '1'), ('ElectricLine', 'Asset type', '电压', None)]
for codedDomainName, content in codedDomains.items():
    arcpy.CreateDomain_management(fgdb, codedDomainName, content[0],"SHORT","CODED")
    for i, name in enumerate(content[1]):   # enumerate是一个python字典的小技巧，同时返回序号(0,1,2...)和value
        arcpy.AddCodedValueToDomain_management(fgdb, codedDomainName, i, name)
for domainField in assignDomainField:
    # *domainField 等同于 domainField[0],domainField[1],domainField[2],domainField[3]
    arcpy.AssignDomainToField_management(*domainField)

# ---------------------改到这里

# 添加终端
arcpy.AddTerminalConfiguration_un(un,"config1","DIRECTIONAL",'A true;B true;C false','Top A-B;Bottom A-C','Bottom')
arcpy.SetTerminalConfiguration_un(un,"Electric","ElectricDevice","变压器","高压","config1")

arcpy.AddTerminalConfiguration_un(un,"config2","DIRECTIONAL",'A true;B true;C false','Top A-B;Bottom A-C','Top')
arcpy.SetTerminalConfiguration_un(un,"Electric","ElectricDevice","变压器","中压","config2")

# 添加网络分组
arcpy.AddNetworkCategory_un(un, 'Protective')
arcpy.SetNetworkCategory_un(un, "Electric", "ElectricDevice", "变压器", "高压变压器","Protective")
arcpy.SetNetworkCategory_un(un, "Electric", "ElectricDevice", "变压器", "中压变压器","Protective")

# 创建关联关系
arcpy.SetAssociationRole_un(un,"Electric","ElectricDevice","变压器","高压变压器","none","RESTRICTED")
arcpy.SetAssociationRole_un(un,"Electric","ElectricDevice","变压器","中压变压器","none","RESTRICTED")
arcpy.SetAssociationRole_un(un,"Electric","ElectricDevice","传输线","高压传输线","none","RESTRICTED")
arcpy.AddRule_un(un,"JUNCTION_EDGE_CONNECTIVITY","ElectricDevice","变压器","高压变压器","ElectricLine","传输线","高压传输线")
arcpy.AddRule_un(un,"JUNCTION_EDGE_CONNECTIVITY","ElectricDevice","传输线","高压传输线","ElectricLine","变压器","中压变压器")
# 设置线联通策略
arcpy.SetEdgeConnectivity_un(un, "Electric","ElectricLine", "传输线","高压传输线", "AnyVertex")

# 添加网络属性，这部分没理解，可选参数domain，是否要关联assettype的属性域
arcpy.AddNetworkAttribute_un(un, "Device Status", "SHORT", "INLINE", "NOT_APPORTIONABLE","","变压器电压", "NOT_OVERRIDABLE")
arcpy.SetNetworkAttribute_un(un,"Device Status","Electric", "ElectricDevice","Asset type")

# 添加层
arcpy.AddTier_un(un,"Electric","高压区",1,"RADIAL")

#设置子网定义
valid_devices = "'变压器/高压'；'变压器/中压'"
valid_lines = "'传输线/高压'"
valid_subnetwork_controller = "变压器/高压'；'变压器/中压'"
aggregated_line = "'传输线/高压'"
diagram_template = "Basic"
arcpy.SetSubnetworkDefinition_un(un,"Electric","高压区","SUPPORT_DISJOINT",
                                valid_devices,valid_subnetwork_controller,valid_lines,aggregated_line,diagram_template,
                                include_barriers="INCLUDE_BARRIERS",traversability_scope="BOTH_JUNCTIONS_AND_EDGES")

# 添加要素

arcpy.Append_management(elebyq,"ElectricDevice","TEXT","变压器")
arcpy.Append_management(elecsx,"ElectricLine","TEXT","传输线")

