#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   2.py
@Time    :   2020/07/14 16:24:01
@Author  :   liming 
@Version :   1.0
@Contact :   lim@esrichina.com.cn
'''

import arcpy
import xlrd
import os

def importallsheets(in_excel,out_gdb):
    workbook = xlrd.open_workbook(in_excel)
    # 遍历返回xlrd.sheet.Sheet对象，对象属性name
    sheets = [sheet.name for sheet in workbook.sheets()]
    print('{} sheets found: {}'.format(len(sheets), ','.join(sheets)))
    for sheet in sheets：
    # os.path.join链接目录与文件，validatetablename验证表明与工作空间，返回有效表明。os.path.basename返回最后一个文件或者目录。path以/\结果返回空值。
    out_table = os.path.join(
        out_gdb,
        arcpy.ValidateTableName(
            "{0}_{1}".format(os.path.basename(in_excel),sheet),
            out_gdb))
    print('converting{} to {}'.format(sheet,out_table))
    # 转换各个工作表
    arcpy.ExcelToTable_conversion(in_excel,out_table,sheet)

def displayxy()


    
