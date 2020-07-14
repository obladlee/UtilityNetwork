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
    sheets = [sheet.name for sheet in workbook.sheets()]
    print()
