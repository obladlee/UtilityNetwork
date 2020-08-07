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
arcpy.env.overwriteOutput = True

#设置输入参数
fgdb = "E:/Eleun.gdb"
service_territory = "E:/ArcGIS/ele.gdb/Service_Area"
dataset = "SYSTEM"
un = "ElectricNetwork"
domainNet,domainNetAlias = "Electric",'电网'
elebyq = "E:/ArcGIS/ele.gdb/ele变压器"
elecsx = "E:/ArcGIS/ele.gdb/ele传输线"

arcpy.env.workspace = os.path.join(fgdb, dataset)

# 创建un和结构网络
arcpy.CreateFileGDB_management(os.path.dirname(fgdb), os.path.basename(fgdb))
arcpy.pt.StageUtilityNetwork(fgdb,service_territory,dataset,un) 

# 创建域网络
arcpy.AddDomainNetwork_un(un,domainNet,"PARTITIONED","SOURCE",domainNetAlias)

# 子类由un自动创建，只需要增加内容
# Unknown子类型也由un自动创建 工具对要素的相对路径识别可能有问题，运行中会报错000732，可能是路径长，可能是不识别，改为绝对路径
domainNetSubtypes = {'ElectricDevice':{"1":"变压器"},'ElectricLine':{"1":"传输线"}}
for in_table, subtypes in domainNetSubtypes.items():  # items()是一个python字典的小技巧，同时返回key和value
    for code, name in subtypes.items():
        arcpy.AddSubtype_management(os.path.join(fgdb, dataset, in_table), code, name)
    arcpy.SetDefaultSubtype_management(os.path.join(
        fgdb, dataset, in_table), 1)  # 如果默认子类不是1，这里还需要额外的输入参数

# 创建属性域,添加域值,分配给字段
# 属性域名称:(描述，(从0开始各code的描述)) 注意ASSETTYPE，不要用别名会报错无效的属性域类型
codedDomains = {'电压': ('电压类型', ('Unknown','高压','中压'))}
assignDomainField = [('E:/Eleun.gdb/ElectricDevice', 'ASSETTYPE',
                      '电压', ['1']), ('E:/Eleun.gdb/ElectricLine', 'ASSETTYPE', '电压', None)]
for codedDomainName, content in codedDomains.items():
    arcpy.CreateDomain_management(fgdb, codedDomainName, content[0],"SHORT","CODED")
    for i, name in enumerate(content[1]):   # enumerate是一个python字典的小技巧，同时返回序号(0,1,2...)和value
        arcpy.AddCodedValueToDomain_management(fgdb, codedDomainName, i, name)
for domainField in assignDomainField:
    # *domainField 等同于 domainField[0],domainField[1],domainField[2],domainField[3]
    arcpy.AssignDomainToField_management(*domainField)
    arcpy.AssignDefaultToField_management(domainField[0],domainField[1],1,domainField[3])

# ---------------------改到这里
# 添加终端
addTer = {"config1": ['A True;B False;C False','Top A-B;Bottom A-C', 'Bottom'], "config2": ['A True;B False;C False','Top A-B;Bottom A-C','Top']}
setTer = {"EletricDevice":["变压器","高压"], "ElectricDevice":["变压器", "中压"]}
for name, ter in addTer.items():
    arcpy.AddTerminalConfiguration_un(un,name,"DIRECTIONAL",ter[0],ter[1],ter[2]) 
    for fc, types in setTer.items():
        arcpy.SetTerminalConfiguration_un(un,domainNet,fc,types[0],types[1],name)
        
# 添加网络分组
netCategory = {"Protective":["ElectricDevice","变压器","高压变压器"], "Protective":["ElectiveDevice","变压器","中压变压器"]}
for name, fc in netCategory.items():
    arcpy.AddNetworkCategory_un(un,name) # 一个分组可以对应多个assettype,放在一个for循环会重复创建网络分组name
    arcpy.SetNetworkCategory_un(un,*fc,name)
    
# 创建关联关系
# 想法是基于关联关系,将两个assettype放在一个变量,资产类多的时候并不是通用写法。 就把role、rule分开设置
assoRole = {"none":["ElectricDevice","变压器","高压变压器"],
            "none":["ElectricLine","传输线","高压传输线"],
            }
addRule = {"JUNCTION_EDGE_CONNECTIVITY":[("ElectricDevice","变压器","高压变压器"),("EletricLine","传输线","高压传输线")],
        "JUNCTION_EDGE_CONNECTIVITY":[("EletricDevice","传输线","高压传输线"),("EletricLine","变压器","中压变压器")]}
eleLine = {"EletricLine":[("传输线","高压传输线")]}
for role, fc in assoRole.items():
    arcpy.SetAssociationRole_un(un,domainNet,*fc,name,"RESTRICTED")
for rulename, fc in addRule.items():
    arcpy.AddRule_un(un,rulename,*fc[0],*fc[1])  
for line, linetype in eleLine.items():
    arcpy.SetEdgeConnectivity_un(un,domainNet,line,*linetype[0],"AnyVertex")

# 添加网络属性，这部分没理解，可选参数domain，是否要关联assettype的属性域, 网络属性的用途有点想象不出来,创建un启用拓扑
netattr = {"Devices Ststus":["ElectricDevice","ASSETTYPE","电压"]}
for name, attr in netattr.items():
    arcpy.AddNetworkAttribute_un(un,name,"SHORT","INLINE","NOT_APP","attr[2]","NOT_OVEREIDABLE")
    arcpy.SetNetworkAttribute_un(un,name,domainNet,attr[0],attr[1])

# 添加层
tier = {"高压层":["1","RADIAL"],"中压层":["1","MESH"]}
for name, rank_type in tier.items():
    arcpy.AddTier_un(un,domainNet,name,rank_type[0],rank_type[1])

#设置子网定义
valid_devices = "'变压器/高压'；'变压器/中压'"
valid_lines = "'传输线/高压'"
valid_subnetwork_controller = "变压器/高压'；'变压器/中压'"
aggregated_line = "'传输线/高压'"
diagram_template = "Basic"
arcpy.SetSubnetworkDefinition_un(un,domainNet,"高压区","SUPPORT_DISJOINT",
                                valid_devices,valid_subnetwork_controller,valid_lines,aggregated_line,diagram_template,
                                include_barriers="INCLUDE_BARRIERS",traversability_scope="BOTH_JUNCTIONS_AND_EDGES")

# 添加要素
featureClass = {elebyq:["EletricDevice","变压器"],elecsx:["EletricLine","传输线"]}
for fc, fc_type in featureClass.items():
    arcpy.Append_management(fc,fc_type[0],"TEXT",fc_type[1])