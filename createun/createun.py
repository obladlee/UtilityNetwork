# coding=utf-8
# __author__ = 'MoaiStone'
# __version__ = 0.1.5
# __date__ = 2020-8-12

import arcpy
import os
import json
import csv
from collections import namedtuple

def createUN(jsonFile, outGDB):
    cfgStr = open(jsonFile, 'r', encoding='gbk').read()
    unObj = json.loads(cfgStr)
    unName = unObj["unName"]
    # 创建un和结构网络
    arcpy.env.preserveGlobalIds = True
    arcpy.env.overwriteOutput = True
    arcpy.CreateFileGDB_management(os.path.dirname(outGDB), os.path.basename(outGDB))
    arcpy.pt.StageUtilityNetwork(outGDB,unObj["territoryFeaCls"],unObj["feaDS"],unName)
    # Tips:尽量使用相对路径，如有工具不支持再改用绝对路径
    arcpy.env.workspace = os.path.join(outGDB, unObj["feaDS"])
    
    # 导入fieldDomains，domain是面向GDB级的物理设置
    for domain in unObj["fieldDomains"]:
        dName = domain["name"]
        if domain.get("dtype") == "RANGE": 
            arcpy.CreateDomain_management(outGDB, dName, domain.get("desc",dName), domain.get("ftype","SHORT"), "RANGE")
            arcpy.SetValueForRangeDomain_management(outGDB, dName, domain['min'], domain['max'])
            continue
        table = arcpy.management.CreateTable('in_memory', dName)[0] # ？[0]
        arcpy.AddField_management(table, 'code', domain.get("ftype","SHORT"))
        arcpy.AddField_management(table, 'name', 'TEXT', field_length=254)
        with arcpy.da.InsertCursor(table, ('code','name')) as cur:
            for v in domain["values"]:
                cur.insertRow((v["code"], v["name"]))
        arcpy.TableToDomain_management(table, 'code', 'name', outGDB, dName, domain.get("desc",dName), update_option='REPLACE')
        arcpy.Delete_management(table)
    
    # 创建除了structure以外的域网络
    for dnObj in unObj["domainNetworks"]:
        if dnObj["name"].lower() != "structure": 
            arcpy.AddDomainNetwork_un(unName, dnObj["name"], dnObj["tierDef"], dnObj["controllerType"], dnObj.get("alias"))

    # 添加TerminalConfiguration,categories,netAttributes，这些是面向整个UN级的逻辑设置
    # Tips:需要先创建至少一个域网络，才能添加TerminalConfiguration
    terminalConfigs = unObj.get("terminalConfigs")
    if terminalConfigs:
        for terminalCfg in terminalConfigs:
            if terminalCfg["dir"] == "DIRECTIONAL":
                arcpy.AddTerminalConfiguration_un(unName, terminalCfg["name"], "DIRECTIONAL",
                    terminals_directional=terminalCfg["terminals"], valid_paths=terminalCfg["paths"], default_path=terminalCfg.get("default"))
            else:
                arcpy.AddTerminalConfiguration_un(unName, terminalCfg["name"], "BIDIRECTIONAL",
                    terminals_bidirectional=terminalCfg["terminals"], valid_paths=terminalCfg["paths"], default_path=terminalCfg.get("default"))
    # TODO: 网络分组与分层的区别?
    categories = unObj.get("categories")
    if categories: ## 为什么加这种判断
        for category in categories:
            arcpy.AddNetworkCategory_un(unName, category)
    # TODO：网络属性的可选设置有什么作用？
    netAttributes = unObj.get("netAttributes")
    if netAttributes:
        for attrib in netAttributes:
            arcpy.AddNetworkAttribute_un(unName, attrib["name"], attrib["type"], attrib.get("inline"),
                attrib.get("apportionable"), attrib.get("domain"), attrib.get("overridable"),
                attrib.get("nullable"), attrib.get("substitution"), attrib.get("attrToSubstitution"))

    # 添加子类，创建新字段，指定属性域，指定网络属性，这些是面向Table级的物理设置
    for dnObj in unObj["domainNetworks"]:
        # 子类已经自动设置为ASSETGROUP字段，添加自定义值
        subtypes = dnObj.get("subtypes")
        if subtypes:
            for subtype in subtypes:
                for v in subtype["values"]:
                    arcpy.AddSubtype_management(subtype["feaCls"], v["code"], v["name"])
                if subtype.get("default"):
                    arcpy.SetDefaultSubtype_management(subtype["feaCls"], subtype.get("default"))
        # 添加自定义字段
        newFields = dnObj.get("newFields")
        if newFields:
            for field in newFields:
                length = field.get("length") if field["type"].upper() == "TEXT" else None
                arcpy.AddField_management(field["feaCls"], field["name"], field["type"], field_length=length,field_alias=field.get("alias"))
        # 为字段指定属性域
        fDomains = dnObj.get("fieldDomains")
        if fDomains:
            for fd in fDomains:
                arcpy.AssignDomainToField_management(fd["feaCls"], fd["fieldName"], fd["domainName"], fd.get("subtypeCodes"))
                if fd.get("default"):
                    arcpy.AssignDefaultToField_management(fd["feaCls"], fd["fieldName"], fd["default"], fd.get("subtypeCodes"))
        # 为字段指定网络属性
        netAttributes = dnObj.get("netAttributes")
        if netAttributes:
            for attribute in netAttributes:
                for field in attribute["fields"]:
                    fc, fName = field.split("/")
                    fObj = arcpy.ListFields(fc, fName)
                    if fObj:
                        arcpy.SetNetworkAttribute_un(unName, attribute["name"], dnObj["name"], fc, fName)

    # 为资产指定多项配置：端子配置、分组、边连通性、角色，这些是面向资产级的逻辑设置
    with open(unObj.get("assetsCSV","not exist"), 'r', encoding='gbk') as fp:
        reader = csv.reader(fp) # 读取列为列表
        header = next(reader)   # ['domainNet', 'feaCls', 'assetName', 'categories', 'terminalCfg', 'edgeConnectivity', 'roleType', 'deletionType', 'viewScale', 'splitType']
        assetCfg = namedtuple('assetCfg', header)
        for row in reader:
            row = assetCfg(*row)
            asset = row.assetName.split('/')
            if row.terminalCfg:
                arcpy.SetTerminalConfiguration_un(unName, row.domainNet, row.feaCls, *asset, row.terminalCfg)
            if row.categories:
                arcpy.SetNetworkCategory_un(unName, row.domainNet, row.feaCls, *asset, row.categories)
            if row.edgeConnectivity: # 边联通非空
                arcpy.SetEdgeConnectivity_un(unName, row.domainNet, row.feaCls, *asset, row.edgeConnectivity)
            if row.roleType:
                arcpy.SetAssociationRole_un(unName, row.domainNet, row.feaCls, *asset, row.roleType, row.deletionType, row.viewScale, row.splitType)

    # 创建tier，并设置子网定义，这些是面向子网级的逻辑设置
    # TODO: subnetwork_field_name有什么作用？subnetDef还有很多可选设置
    for dnObj in unObj["domainNetworks"]:
        dnName = dnObj["name"]
        if dnName.lower() != "structure":
            # tierGroups
            tierGroups = dnObj.get("tierGroups")
            if tierGroups and dnObj["tierDef"]=="HIERARCHICAL":
                for groupName in tierGroups:
                    arcpy.AddTierGroup_un(unName, dnName, groupName)
            tiers = dnObj.get("tiers")
            if tiers:
                for tier in tiers:
                    if dnObj["tierDef"]=="HIERARCHICAL":
                        arcpy.AddTier_un(unName, dnName, tier["name"], tier["rank"], topology_type="MESH",tier_group_name=tier.get("groupName"),subnetwork_field_name=tier["subnetField"])
                    else:
                        arcpy.AddTier_un(unName, dnName, tier["name"], tier["rank"], topology_type=tier["topo"])
                    arcpy.SetSubnetworkDefinition_un(unName, dnName, tier["name"], tier["disjoint"],
                                tier["devices"],tier["controllers"],tier.get("lines"),tier.get("aggregated"),
                                tier.get("diagrams"),include_barriers=tier.get("barriers"),traversability_scope=tier.get("traverse"))

    # TODO: 导入rule
    arcpy.ImportRules_un(unName,"All","E:/ArcGIS/unnet/rules.csv")
    # TODO: 导入数据
    # 数据导入是基于子类的，把要素类路径写入到子类中，修改了demoUN域网络的子类型值
    for dnObj in unObj["domainNetworks"]:
        subtypes = dnObj.get("subtypes")
        if subtypes:
            for subtype in subtypes:
                for v in subtype["values"]:
                    arcpy.Append_management(subtype["path"],subtype["feaCls"],"NO_TEST",subtype=v["name"])
    # TODO: 导入关联关系

    # TODO: 导入子网控制器
    # arcpy.ImportSubnetworkControllers_un(unName,"E:/ArcGIS/unnet/subnetwork_controllers.csv")
    

if __name__ == "__main__":
    createUN(r"E:\ArcGIS\unnet\demoUN.json", r"E:\ArcGIS\unnet\elecDemo.gdb")

    