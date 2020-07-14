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
import untools

arcpy.env.preserveGlobalIds = True
arcpy.env.workspace = "E:/ArcGIS/pro_Projects/Eleun/Eleun.gdb"

#设置局部变量
fgdb = "E:/ArcGIS/pro_Projects/Eleun/Eleun.gdb"
service_territory = "E:/ArcGIS/pro_Projects/Eleun/Eleun.gdb/Service_Area"
dataset = "SYSTEM"
network_name = "ElectricNetwork"
# elebyq = "E:/ArcGIS/pro_Projects/Eleun/ele变压器"
# elecsx = "E:/ArcGIS/pro_Projects/Eleun/ele传输线"

arcpy.pt.StageUtilityNetwork(fgdb,service_territory,dataset,network_name) 
# try:
# 创建域网络,创建域出错几次，再次运行代码，会重新创建un，且以un_1/2..命名要素
arcpy.AddDomainNetwork_un("ElectricNetwork","Electric","PARTITIONED","SOURCE","Electric_alias")
# except arcpy.ExecuteError:
#     arcpy.AddError(arcpy.GetMessage(2))
# except:
#     e = sys.exc_info()[1]
#     print(e.args[0])
    
# 添加子类型
arcpy.SetSubtypeField_management("ElectricDevice","Asset group")
stypeDict = {"0":"Unknown","1":"变压器"}
for code in stypeDict:
    arcpy.AddSubtype_management("ElectricDevice",code,stypeDict[code])
arcpy.SetDefaultSubtype_management("ElectricDevice",1)

arcpy.SetSubtypeField_management("ElectricLine","Asset group")
stypeDict1 = {"0":"Unknown","1":"传输线"}
for code in stypeDict1:
    arcpy.addSubtype_management("ElectricLine",code,stypeDict1[code])
arcpy.SetDefaultSubtype_management("ElectricLine",1)

#创建属性域,添加域值，分配给字段
#创建变压器属性域
arcpy.CreateDomain_management(fgdb,"变压器电压","变压器电压类型","SHORT","CODED")
domDict = {
    "1":"y=高压","2":"中压"
}
for code in domDict:
    arcpy.AddCodedValueToDomain_management(fgdb,"变压器电压",code,domDict[code])
arcpy.AssignDomainToField_management("ElectricDevice","Asset type","变压器电压")

#创建传输线属性域
arcpy.CreateDomain_management(fgdb,"传输线电压","传输线电压类型","SHORT","CODED")
domDict1 = {
    "1":"高压"
}
for code in domDict:
    arcpy.AddCodedValueToDomain_management(fgdb,"传输线电压",code,domDict[code])
arcpy.AssignDomainToField_management("ElectricLine","Asset type","变压器电压")

# 添加终端
arcpy.AddTerminalConfiguration_un(network_name,"config1","DIRECTIONAL",'A true;B true;C false','Top A-B;Bottom A-C','Bottom')
arcpy.SetTerminalConfiguration_un(network_name,"Electric","ElectricDevice","变压器","高压","config1")

arcpy.AddTerminalConfiguration_un(network_name,"config2","DIRECTIONAL",'A true;B true;C false','Top A-B;Bottom A-C','Top')
arcpy.SetTerminalConfiguration_un(network_name,"Electric","ElectricDevice","变压器","中压","config2")

# 添加网络分组
arcpy.AddNetworkCategory_un(network_name, 'Protective')
arcpy.SetNetworkCategory_un(network_name, "Electric", "ElectricDevice", "变压器", "高压变压器","Protective")
arcpy.SetNetworkCategory_un(network_name, "Electric", "ElectricDevice", "变压器", "中压变压器","Protective")

# 创建关联关系
arcpy.SetAssociationRole_un(network_name,"Electric","ElectricDevice","变压器","高压变压器","none","RESTRICTED")
arcpy.SetAssociationRole_un(network_name,"Electric","ElectricDevice","变压器","中压变压器","none","RESTRICTED")
arcpy.SetAssociationRole_un(network_name,"Electric","ElectricDevice","传输线","高压传输线","none","RESTRICTED")
arcpy.AddRule_un(network_name,"JUNCTION_EDGE_CONNECTIVITY","ElectricDevice","变压器","高压变压器","ElectricLine","传输线","高压传输线")
arcpy.AddRule_un(network_name,"JUNCTION_EDGE_CONNECTIVITY","ElectricDevice","传输线","高压传输线","ElectricLine","变压器","中压变压器")
# 设置线联通策略
arcpy.SetEdgeConnectivity_un(network_name, "Electric","ElectricLine", "传输线","高压传输线", "AnyVertex")

# 添加网络属性，这部分没理解，可选参数domain，是否要关联assettype的属性域
arcpy.AddNetworkAttribute_un(network_name, "Device Status", "SHORT", "INLINE", "NOT_APPORTIONABLE","","变压器电压", "NOT_OVERRIDABLE")
arcpy.SetNetworkAttribute_un(network_name,"Device Status","Electric", "ElectricDevice","Asset type")

# 添加层
arcpy.AddTier_un(network_name,"Electric","高压区",1,"RADIAL")

#设置子网定义
valid_devices = "'变压器/高压'；'变压器/中压'"
valid_lines = "'传输线/高压'"
valid_subnetwork_controller = "变压器/高压'；'变压器/中压'"
aggregated_line = "'传输线/高压'"
diagram_template = "Basic"
arcpy.SetSubnetworkDefinition_un(network_name,"Electric","高压区","SUPPORT_DISJOINT",
                                valid_devices,valid_subnetwork_controller,valid_lines,aggregated_line,diagram_template,
                                include_barriers="INCLUDE_BARRIERS",traversability_scope="BOTH_JUNCTIONS_AND_EDGES")

# 添加要素

arcpy.Append_management(elebyq,"ElectricDevice","TEXT","变压器")
arcpy.Append_management(elecsx,"ElectricLine","TEXT","传输线")

