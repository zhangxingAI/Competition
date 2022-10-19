import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from PIL import Image, ImageDraw
import os
from pulp import *
import gurobipy as grb
"""
读取原数据，对原数据以长宽比进行排序，输出item信息（长，宽，id号，订单批次，订单材质）
"""
def add_area(url):
    df1 = pd.read_csv(url, engine='python', on_bad_lines='skip')
    df = sort(df1)
    ls = []
    for i, j in zip(df['item_length'].tolist(), df['item_width'].tolist()):
        k = i * j
        ls.append(k)
    df['area'] = ls
    return df
def read(df):
    df1 =df
    ls = []
    xls=[]
    yls=[]
    for i, j in zip(df1['item_length'].tolist(), df1['item_width'].tolist()):
        k = min(i, j) / max(i, j)
        ls.append(k)
    df1.insert(df1.shape[1], '尺寸', ls)
    # df1['尺寸'] = ls
    df2 = df1.sort_values(by=['尺寸'],ascending = False)
    # print(df)
    for i, j in zip(df2['item_length'].tolist(), df2['item_width'].tolist()):
        x = max(i, j)
        y = min(i, j)
        xls.append(x)
        yls.append(y)
    result = zip(xls, yls, df2['item_id'],df2['订单批次'],df2['item_material'])

    # result = zip(df['item_length'].tolist(),df['item_width'].tolist(),df['item_id'])
    return list(result)
def read_pre(df):
    df1 = df
    ls = []
    xls = []
    yls = []
    for i, j in zip(df1['item_length'].tolist(), df1['item_width'].tolist()):
        k = min(i, j) / max(i, j)
        ls.append(k)
    df1.insert(df1.shape[1], '尺寸', ls)
    df1.insert(df1.shape[1], '订单批次', ls)
    # df1['尺寸'] = ls
    df2 = df1.sort_values(by=['尺寸'], ascending=False)
    # print(df)
    for i, j in zip(df2['item_length'].tolist(), df2['item_width'].tolist()):
        x = max(i, j)
        y = min(i, j)
        xls.append(x)
        yls.append(y)
    result = zip(xls, yls, df2['item_id'], df2['订单批次'], df2['item_material'])

    # result = zip(df['item_length'].tolist(),df['item_width'].tolist(),df['item_id'])
    return list(result)
"""
按特定规则对数据排序
"""
def sort(df):
    df1 = df.sort_values(by=['item_material'])
    return df1
"""
从订单池中提取list中对应的订单
"""
def output(list,df):
    pick = df.loc[df['item_order'].isin(list)]
    return pick
"""
计算每个批次的板材使用率
"""
def waste(x,df):
    container_num = 0
    spaceused = 0
    B2_record_ls = []
    df_pick = output(x, df)
    record_ls = exctitem(df_pick)
    for i in record_ls:
        objects = read_pre(i)
        B2_record, containerused, space = record(objects)
        B2_record_ls.append(B2_record)
        container_num += containerused
        spaceused += space
    useeff = spaceused / (container_num * 2440 * 1220)
    return useeff
"""
记录数据集中的订单名称
"""
def order_record(df):
    item_num = []
    area = []
    ls = df['item_order'].tolist()
    item_order = list(set(ls))
    item_order.sort(key=ls.index)
    for i in item_order:
        df1 = df.loc[df['item_order'] == i]
        item_num.append(sum(df1['item_num'].tolist()))
        area.append(sum(df1['area'].tolist()))
    # item_num = list(df.groupby(by=['item_order'])['item_num'].sum())
    # item_order = list(df.groupby(by=['item_order'])['item_num'].sum().index)
    # area = list(df.groupby(by=['item_order'])['area'].sum())
    return item_order,item_num,area
"""
若订单已分配，从未分配订单池中移除
"""
def remove(pick,item_order,item_num,area):
    for i in pick:
        index = item_order.index(i)
        item_order.remove(item_order[index])
        item_num.remove(item_num[index])
        area.remove(area[index])
    return item_order,item_num,area
"""
创建系数列表，返回[k,k,...,k]
"""
def creatcof(n,k):
    x = [[] for x in range(n)]
    for i in range(n):
        x[i] = k
    return x
"""
计算单块原片的剩余可用面积
"""
def spaceleft(widthleft,heightleft,height):
    space = widthleft * (height - heightleft) + heightleft * containerSize[0]
    return space
"""
计算订单的板材利用率
"""
def usage(width, height, n, objects):
    space = 0

    for obj in objects:
        space += obj[0] * obj[1]

    usage = round(space/(width * height * n),4)

    return usage
"""
原片切割算法，并记录玻璃片的切割坐标、x方向长度、y方向长度、所属原片编号等信息，最终返回一个记录切割玻璃片的df数据库
"""
def record(objects):
    containersUsed = 1
    widthLeft = containerSize[0]
    heightLeft = containerSize[1]

    rowHeight = 0
    rowHeight_record = 0
    item_id = []
    x = []
    y = []
    X = []
    Y = []
    container_id = []
    item_material = []
    contain = []
    new_con = []
    batch =[]

    for obj in objects:
        index = 0
        flag = False
        for i in contain:
            if obj[0] < i[4] and obj[1] < i[3]:
                container_id.append(i[0])
                X.append(i[1])
                Y.append(i[2])
                x.append(obj[1])
                y.append(obj[0])
                item_id.append(obj[2])
                item_material.append(obj[4])
                batch.append(obj[3])
                j = list(i)
                j[1] = j[1] + obj[1]
                j[3] = j[3] - obj[1]
                contain[index] = tuple(j)
                flag = True
                break

            elif obj[0] < i[3] and obj[1] < i[4]:
                container_id.append(i[0])
                X.append(i[1])
                Y.append(i[2])
                x.append(obj[0])
                y.append(obj[1])
                item_id.append(obj[2])
                item_material.append(obj[4])
                batch.append(obj[3])
                j = list(i)
                j[1] = j[1] + obj[0]
                j[3] = j[3] - obj[0]
                contain[index] = tuple(j)
                flag = True
                break
            else:
                index += 1

        if flag:
            continue

        if obj[0] <= widthLeft and obj[0] <= heightLeft and \
                spaceleft(widthLeft - obj[0], min(heightLeft - rowHeight, heightLeft - obj[1]), heightLeft) \
                < \
                spaceleft(widthLeft - obj[1], min(heightLeft - rowHeight, heightLeft - obj[0]), heightLeft):
            widthLeft -= obj[1]
            rowHeight = max(rowHeight, obj[0])
            X.append(containerSize[0] - widthLeft - obj[1])
            Y.append(rowHeight_record)
            x.append(obj[1])
            y.append(obj[0])
            container_id.append(containersUsed)
            item_id.append(obj[2])
            item_material.append(obj[4])
            batch.append(obj[3])


        elif obj[1] <= widthLeft and obj[0] > widthLeft and obj[0] <= heightLeft and obj[1] <= (heightLeft-rowHeight) and \
             spaceleft(containerSize[0] - obj[0], heightLeft-rowHeight-obj[1], heightLeft-rowHeight) \
             < \
             spaceleft(widthLeft - obj[1], min(heightLeft - rowHeight, heightLeft- obj[0]),heightLeft):
            widthLeft -= obj[1]
            rowHeight = max(rowHeight, obj[0])
            X.append(containerSize[0] - widthLeft - obj[1])
            Y.append(rowHeight_record)
            x.append(obj[1])
            y.append(obj[0])
            container_id.append(containersUsed)
            item_id.append(obj[2])
            item_material.append(obj[4])
            batch.append(obj[3])

        elif obj[0] <= widthLeft and obj[1] <= heightLeft:
            widthLeft -= obj[0]
            rowHeight = max(rowHeight, obj[1])
            X.append(containerSize[0] - widthLeft - obj[0])
            Y.append(rowHeight_record)
            x.append(obj[0])
            y.append(obj[1])
            container_id.append(containersUsed)
            item_id.append(obj[2])
            item_material.append(obj[4])
            batch.append(obj[3])

            # 增加新行
        elif obj[0] > widthLeft and obj[1] <= (heightLeft - rowHeight):
            new_con.append(
                (containersUsed, containerSize[0] - widthLeft, rowHeight_record, widthLeft, rowHeight))

            widthLeft = containerSize[0] - obj[0]

            rowHeight_record += rowHeight
            heightLeft -= rowHeight
            rowHeight = obj[1]
            X.append(containerSize[0] - widthLeft - obj[0])
            Y.append(rowHeight_record)
            x.append(obj[0])
            y.append(obj[1])
            container_id.append(containersUsed)
            item_id.append(obj[2])
            item_material.append(obj[4])
            batch.append(obj[3])

        elif obj[1] <= widthLeft and obj[0] > widthLeft and obj[0] <= heightLeft and obj[1] > (heightLeft-rowHeight):
            widthLeft -= obj[1]
            rowHeight = max(rowHeight, obj[0])
            X.append(containerSize[0] - widthLeft - obj[1])
            Y.append(rowHeight_record)
            x.append(obj[1])
            y.append(obj[0])
            container_id.append(containersUsed)
            item_id.append(obj[2])
            item_material.append(obj[4])
            batch.append(obj[3])

        # 增加新原片
        else:
            new_con.append(
                (containersUsed, containerSize[0] - widthLeft, rowHeight_record, widthLeft, rowHeight))
            new_con.append(
                (containersUsed, 0, rowHeight+rowHeight_record, containerSize[0], heightLeft - rowHeight))
            contain = contain + new_con
            new_con = []
            widthLeft = containerSize[0] - obj[0]
            heightLeft = containerSize[1]
            rowHeight = obj[1]
            rowHeight_record = 0
            containersUsed += 1
            X.append(containerSize[0] - widthLeft - obj[0])
            Y.append(rowHeight_record)
            x.append(obj[0])
            y.append(obj[1])
            container_id.append(containersUsed)
            item_id.append(obj[2])
            item_material.append(obj[4])
            batch.append(obj[3])
    # 输出方案
    df = pd.DataFrame(list(zip(batch,item_material, container_id, item_id, X, Y, x, y)),
                      columns=['批次序号','原片材质', '原片序号', '产品id', '产品x坐标', '产品y坐标', '产品x方向长度', '产品y方向长度'])
    containersUsed = max(df['原片序号'].tolist())
    efficiency = usage(containerSize[0], containerSize[1], containersUsed, objects)
    spaceused = efficiency*containersUsed*containerSize[0]*containerSize[1]
    # print("原片总数: ", containersUsed)
    # print("板材利用率: ", efficiency)
    # print(df)
    # df3 = df['产品id']
    # print(df3.duplicated().sum())
    return df,containersUsed,spaceused
"""
单次订单分配算法模块，输出订单名集合的列表
"""
def solve(df):
    w = []
    w1 = item_order[0:1]
    u=0
    j1,j2,j3,j4,j5,j6,j7,j8,j9 = 0,0,0,0,0,0,0,0,0
    u1 = waste(w1,df)
    if len(item_order)>=9:
        for i1 in range(1,len(item_order)):
            w2 = [item_order[0],item_order[i1]]
            if item_num[0]+item_num[i1]<=1000 and area[0]+area[i1]<=250000000:
                u2 = waste(w2,df)
                if u>=u2:
                    w = w1
                    u = u1
                    # print('板材利用率：',u)
                    break
                else:
                    w = w2
                    j1 = i1
                    u= u2
                    for i2 in range(1,len(item_order)):
                        w3 = [item_order[0], item_order[j1],item_order[i2]]
                        if item_num[0] + item_num[j1] +item_num[i2]<= 1000 and area[0] + area[j1] + area[i2]<= 250000000 and i2!=j1:
                            u3 = waste(w3,df)
                            if u>=u3:
                                # print('板材利用率：', u)
                                break
                            else:
                                w = w3
                                j2 = i2
                                u = u3
                                for i3 in range(1, len(item_order)):
                                    w4 = [item_order[0], item_order[j1], item_order[j2],item_order[i3]]
                                    if item_num[0] + item_num[j1] + item_num[j2] + item_num[i3]<= 1000 and area[0] + area[
                                        j1] + area[j2] + area [i3] <= 250000000 and i3 != j1 and i3!= j2:
                                        u4 = waste(w4, df)
                                        if u >= u4:
                                            # print('板材利用率：', u)
                                            break
                                        else:
                                            w = w4
                                            j3 = i3
                                            u = u4
                                            for i4 in range(1, len(item_order)):
                                                w5 = [item_order[0], item_order[j1], item_order[j2], item_order[j3],item_order[i4]]
                                                if item_num[0] + item_num[j1] + item_num[j2] + item_num[j3] +item_num[i4] <= 1000 and \
                                                        area[0] + area[j1] + area[j2] + area[j3] + area[i4]<= 250000000 and i4 != j1 and\
                                                        i4 != j2 and i4 != j3:
                                                    u5 = waste(w5, df)
                                                    if u >= u5:
                                                        # print('板材利用率：', u)
                                                        break
                                                    else:
                                                        w = w5
                                                        j4 = i4
                                                        u = u5
                                                        for i5 in range(1, len(item_order)):
                                                            w6 = [item_order[0], item_order[j1], item_order[j2],
                                                                  item_order[j3], item_order[j4], item_order[i5]]
                                                            if item_num[0] + item_num[j1] + item_num[j2] + item_num[j3] + \
                                                                    item_num[j4] +item_num[i5] <= 1000 and \
                                                                    area[0] + area[j1] + area[j2] + area[j3] + area[
                                                                j4] +area[i5] <= 250000000 and i5 != j1 and \
                                                                    i5 != j2 and i5 != j3 and i5!=j4:
                                                                u6 = waste(w6, df)
                                                                if u >= u6:
                                                                    # print('板材利用率：', u)
                                                                    break
                                                                else:
                                                                    w = w6
                                                                    j5 = i5
                                                                    u = u6
                                                                    for i6 in range(1, len(item_order)):
                                                                        w7 = [item_order[0], item_order[j1],
                                                                              item_order[j2],
                                                                              item_order[j3], item_order[j4],
                                                                              item_order[j5],item_order[i6]]
                                                                        if item_num[0] + item_num[j1] + item_num[j2] + \
                                                                                item_num[j3] + \
                                                                                item_num[j4] + item_num[j5] +item_num[i6] <= 1000 and \
                                                                                area[0] + area[j1] + area[j2] + area[
                                                                            j3] + area[
                                                                            j4] + area[j5] +area[i6]<= 250000000 and i6 != j1 and \
                                                                                i6 != j2 and i6 != j3 and i6 != j4 and i6 != j5:
                                                                            u7 = waste(w7, df)
                                                                            if u >= u7:
                                                                                # print('板材利用率：', u)
                                                                                break
                                                                            else:
                                                                                w = w7
                                                                                j6 = i6
                                                                                u = u7
                                                                                for i7 in range(1, len(item_order)):
                                                                                    w8 = [item_order[0], item_order[j1],
                                                                                          item_order[j2],
                                                                                          item_order[j3],
                                                                                          item_order[j4],
                                                                                          item_order[j5],
                                                                                          item_order[j6],
                                                                                          item_order[i7]]
                                                                                    if item_num[0] + item_num[j1] + \
                                                                                            item_num[j2] + \
                                                                                            item_num[j3] + \
                                                                                            item_num[j4] + item_num[
                                                                                        j5] + item_num[j6] + item_num[i7] <= 1000 and \
                                                                                            area[0] + area[j1] + area[
                                                                                        j2] + area[
                                                                                        j3] + area[
                                                                                        j4] + area[j5] + area[
                                                                                        j6] + area[i7]<= 250000000 and i7 != j1 and \
                                                                                            i7 != j2 and i7 != j3 and i7 != j4 and i7 != j5 and i7 != j6:
                                                                                        u8 = waste(w8, df)
                                                                                        if u >= u8:
                                                                                            # print('板材利用率：', u)
                                                                                            break
                                                                                        else:
                                                                                            w = w8
                                                                                            j7 = i7
                                                                                            u = u8
                                                                                            for i8 in range(1,
                                                                                                            len(item_order)):
                                                                                                w9 = [item_order[0],
                                                                                                      item_order[j1],
                                                                                                      item_order[j2],
                                                                                                      item_order[j3],
                                                                                                      item_order[j4],
                                                                                                      item_order[j5],
                                                                                                      item_order[j6],
                                                                                                      item_order[j7],
                                                                                                      item_order[i8]]
                                                                                                if item_num[0] + \
                                                                                                        item_num[j1] + \
                                                                                                        item_num[j2] + \
                                                                                                        item_num[j3] + \
                                                                                                        item_num[j4] + \
                                                                                                        item_num[
                                                                                                            j5] + \
                                                                                                        item_num[j6] + \
                                                                                                        item_num[
                                                                                                            j7] + item_num[i8]<= 1000 and \
                                                                                                        area[0] + area[
                                                                                                    j1] + area[
                                                                                                    j2] + area[
                                                                                                    j3] + area[
                                                                                                    j4] + area[j5] + \
                                                                                                        area[
                                                                                                            j6] + area[
                                                                                                    j7] +area[i8]<= 250000000 and i8 != j1 and \
                                                                                                        i8 != j2 and i8 != j3 and i8 != j4 and i8 != j5 and i8 != j6 and i8!=j7:
                                                                                                    u9 = waste(w9, df)
                                                                                                    if u >= u9:
                                                                                                        # print('板材利用率：',
                                                                                                        #       u)
                                                                                                        break
                                                                                                    else:
                                                                                                        w = w9
                                                                                                        j8 = i8
                                                                                                        u = u9
                                                                                                        # print('板材利用率：',
                                                                                                        #       u)
                                                                                                        break
                                                                                        break
                                                                            break
                                                                break

                                                    break
                                        break
                            break
                break
    elif len(item_order) ==8:
        for i1 in range(1,len(item_order)):
            w2 = [item_order[0],item_order[i1]]
            if item_num[0]+item_num[i1]<=1000 and area[0]+area[i1]<=250000000:
                u2 = waste(w2,df)
                if u>=u2:
                    w = w1
                    u = u1
                    # print('板材利用率：', u)
                    break
                else:
                    w = w2
                    j1 = i1
                    u= u2
                    for i2 in range(1,len(item_order)):
                        w3 = [item_order[0], item_order[j1],item_order[i2]]
                        if item_num[0] + item_num[j1] +item_num[i2]<= 1000 and area[0] + area[j1] + area[i2]<= 250000000 and i2!=j1:
                            u3 = waste(w3,df)
                            if u>=u3:
                                # print('板材利用率：', u)
                                break
                            else:
                                w = w3
                                j2 = i2
                                u = u3
                                for i3 in range(1, len(item_order)):
                                    w4 = [item_order[0], item_order[j1], item_order[j2],item_order[i3]]
                                    if item_num[0] + item_num[j1] + item_num[j2] + item_num[i3]<= 1000 and area[0] + area[
                                        j1] + area[j2] + area [i3] <= 250000000 and i3 != j1 and i3!= j2:
                                        u4 = waste(w4, df)
                                        if u >= u4:
                                            # print('板材利用率：', u)
                                            break
                                        else:
                                            w = w4
                                            j3 = i3
                                            u = u4
                                            for i4 in range(1, len(item_order)):
                                                w5 = [item_order[0], item_order[j1], item_order[j2], item_order[j3],item_order[i4]]
                                                if item_num[0] + item_num[j1] + item_num[j2] + item_num[j3] +item_num[i4] <= 1000 and \
                                                        area[0] + area[j1] + area[j2] + area[j3] + area[i4]<= 250000000 and i4 != j1 and\
                                                        i4 != j2 and i4 != j3:
                                                    u5 = waste(w5, df)
                                                    if u >= u5:
                                                        # print('板材利用率：', u)
                                                        break
                                                    else:
                                                        w = w5
                                                        j4 = i4
                                                        u = u5
                                                        for i5 in range(1, len(item_order)):
                                                            w6 = [item_order[0], item_order[j1], item_order[j2],
                                                                  item_order[j3], item_order[j4], item_order[i5]]
                                                            if item_num[0] + item_num[j1] + item_num[j2] + item_num[j3] + \
                                                                    item_num[j4] +item_num[i5] <= 1000 and \
                                                                    area[0] + area[j1] + area[j2] + area[j3] + area[
                                                                j4] +area[i5] <= 250000000 and i5 != j1 and \
                                                                    i5 != j2 and i5 != j3 and i5!=j4:
                                                                u6 = waste(w6, df)
                                                                if u >= u6:
                                                                    # print('板材利用率：', u)
                                                                    break
                                                                else:
                                                                    w = w6
                                                                    j5 = i5
                                                                    u = u6
                                                                    for i6 in range(1, len(item_order)):
                                                                        w7 = [item_order[0], item_order[j1],
                                                                              item_order[j2],
                                                                              item_order[j3], item_order[j4],
                                                                              item_order[j5],item_order[i6]]
                                                                        if item_num[0] + item_num[j1] + item_num[j2] + \
                                                                                item_num[j3] + \
                                                                                item_num[j4] + item_num[j5] +item_num[i6] <= 1000 and \
                                                                                area[0] + area[j1] + area[j2] + area[
                                                                            j3] + area[
                                                                            j4] + area[j5] +area[i6]<= 250000000 and i6 != j1 and \
                                                                                i6 != j2 and i6 != j3 and i6 != j4 and i6 != j5:
                                                                            u7 = waste(w7, df)
                                                                            if u >= u7:
                                                                                # print('板材利用率：', u)
                                                                                break
                                                                            else:
                                                                                w = w7
                                                                                j6 = i6
                                                                                u = u7
                                                                                for i7 in range(1, len(item_order)):
                                                                                    w8 = [item_order[0], item_order[j1],
                                                                                          item_order[j2],
                                                                                          item_order[j3],
                                                                                          item_order[j4],
                                                                                          item_order[j5],
                                                                                          item_order[j6],
                                                                                          item_order[i7]]
                                                                                    if item_num[0] + item_num[j1] + \
                                                                                            item_num[j2] + \
                                                                                            item_num[j3] + \
                                                                                            item_num[j4] + item_num[
                                                                                        j5] + item_num[j6] + item_num[i7] <= 1000 and \
                                                                                            area[0] + area[j1] + area[
                                                                                        j2] + area[
                                                                                        j3] + area[
                                                                                        j4] + area[j5] + area[
                                                                                        j6] + area[i7]<= 250000000 and i7 != j1 and \
                                                                                            i7 != j2 and i7 != j3 and i7 != j4 and i7 != j5 and i7 != j6:
                                                                                        u8 = waste(w8, df)
                                                                                        if u >= u8:
                                                                                            # print('板材利用率：', u)
                                                                                            break
                                                                                        else:
                                                                                            w = w8
                                                                                            j7 = i7
                                                                                            u = u8
                                                                                            # print('板材利用率：', u)

                                                                                        break
                                                                            break
                                                                break

                                                    break
                                        break
                            break
                break
    elif len(item_order)==7:
        for i1 in range(1,len(item_order)):
            w2 = [item_order[0],item_order[i1]]
            if item_num[0]+item_num[i1]<=1000 and area[0]+area[i1]<=250000000:
                u2 = waste(w2,df)
                if u>=u2:
                    w = w1
                    u = u1
                    # print('板材利用率：', u)
                    break
                else:
                    w = w2
                    j1 = i1
                    u= u2
                    for i2 in range(1,len(item_order)):
                        w3 = [item_order[0], item_order[j1],item_order[i2]]
                        if item_num[0] + item_num[j1] +item_num[i2]<= 1000 and area[0] + area[j1] + area[i2]<= 250000000 and i2!=j1:
                            u3 = waste(w3,df)
                            if u>=u3:
                                # print('板材利用率：', u)
                                break
                            else:
                                w = w3
                                j2 = i2
                                u = u3
                                for i3 in range(1, len(item_order)):
                                    w4 = [item_order[0], item_order[j1], item_order[j2],item_order[i3]]
                                    if item_num[0] + item_num[j1] + item_num[j2] + item_num[i3]<= 1000 and area[0] + area[
                                        j1] + area[j2] + area [i3] <= 250000000 and i3 != j1 and i3!= j2:
                                        u4 = waste(w4, df)
                                        if u >= u4:
                                            # print('板材利用率：', u)
                                            break
                                        else:
                                            w = w4
                                            j3 = i3
                                            u = u4
                                            for i4 in range(1, len(item_order)):
                                                w5 = [item_order[0], item_order[j1], item_order[j2], item_order[j3],item_order[i4]]
                                                if item_num[0] + item_num[j1] + item_num[j2] + item_num[j3] +item_num[i4] <= 1000 and \
                                                        area[0] + area[j1] + area[j2] + area[j3] + area[i4]<= 250000000 and i4 != j1 and\
                                                        i4 != j2 and i4 != j3:
                                                    u5 = waste(w5, df)
                                                    if u >= u5:
                                                        # print('板材利用率：', u)
                                                        break
                                                    else:
                                                        w = w5
                                                        j4 = i4
                                                        u = u5
                                                        for i5 in range(1, len(item_order)):
                                                            w6 = [item_order[0], item_order[j1], item_order[j2],
                                                                  item_order[j3], item_order[j4], item_order[i5]]
                                                            if item_num[0] + item_num[j1] + item_num[j2] + item_num[j3] + \
                                                                    item_num[j4] +item_num[i5] <= 1000 and \
                                                                    area[0] + area[j1] + area[j2] + area[j3] + area[
                                                                j4] +area[i5] <= 250000000 and i5 != j1 and \
                                                                    i5 != j2 and i5 != j3 and i5!=j4:
                                                                u6 = waste(w6, df)
                                                                if u >= u6:
                                                                    # print('板材利用率：', u)
                                                                    break
                                                                else:
                                                                    w = w6
                                                                    j5 = i5
                                                                    u = u6
                                                                    for i6 in range(1, len(item_order)):
                                                                        w7 = [item_order[0], item_order[j1],
                                                                              item_order[j2],
                                                                              item_order[j3], item_order[j4],
                                                                              item_order[j5],item_order[i6]]
                                                                        if item_num[0] + item_num[j1] + item_num[j2] + \
                                                                                item_num[j3] + \
                                                                                item_num[j4] + item_num[j5] +item_num[i6] <= 1000 and \
                                                                                area[0] + area[j1] + area[j2] + area[
                                                                            j3] + area[
                                                                            j4] + area[j5] +area[i6]<= 250000000 and i6 != j1 and \
                                                                                i6 != j2 and i6 != j3 and i6 != j4 and i6 != j5:
                                                                            u7 = waste(w7, df)
                                                                            if u >= u7:
                                                                                # print('板材利用率：', u)
                                                                                break
                                                                            else:
                                                                                w = w7
                                                                                j6 = i6
                                                                                u = u7
                                                                                # print('板材利用率：', u)

                                                                            break
                                                                break

                                                    break
                                        break
                            break
                break
    elif len(item_order) == 6:
        for i1 in range(1, len(item_order)):
            w2 = [item_order[0], item_order[i1]]
            if item_num[0] + item_num[i1] <= 1000 and area[0] + area[i1] <= 250000000:
                u2 = waste(w2, df)
                if u >= u2:
                    w = w1
                    u = u1
                    # print('板材利用率：', u)
                    break
                else:
                    w = w2
                    j1 = i1
                    u = u2
                    for i2 in range(1, len(item_order)):
                        w3 = [item_order[0], item_order[j1], item_order[i2]]
                        if item_num[0] + item_num[j1] + item_num[i2] <= 1000 and area[0] + area[j1] + area[
                            i2] <= 250000000 and i2 != j1:
                            u3 = waste(w3, df)
                            if u >= u3:
                                # print('板材利用率：', u)
                                break
                            else:
                                w = w3
                                j2 = i2
                                u = u3
                                for i3 in range(1, len(item_order)):
                                    w4 = [item_order[0], item_order[j1], item_order[j2], item_order[i3]]
                                    if item_num[0] + item_num[j1] + item_num[j2] + item_num[i3] <= 1000 and area[0] + \
                                            area[
                                                j1] + area[j2] + area[i3] <= 250000000 and i3 != j1 and i3 != j2:
                                        u4 = waste(w4, df)
                                        if u >= u4:
                                            # print('板材利用率：', u)
                                            break
                                        else:
                                            w = w4
                                            j3 = i3
                                            u = u4
                                            for i4 in range(1, len(item_order)):
                                                w5 = [item_order[0], item_order[j1], item_order[j2], item_order[j3],
                                                      item_order[i4]]
                                                if item_num[0] + item_num[j1] + item_num[j2] + item_num[j3] + item_num[
                                                    i4] <= 1000 and \
                                                        area[0] + area[j1] + area[j2] + area[j3] + area[
                                                    i4] <= 250000000 and i4 != j1 and \
                                                        i4 != j2 and i4 != j3:
                                                    u5 = waste(w5, df)
                                                    if u >= u5:
                                                        # print('板材利用率：', u)
                                                        break
                                                    else:
                                                        w = w5
                                                        j4 = i4
                                                        u = u5
                                                        for i5 in range(1, len(item_order)):
                                                            w6 = [item_order[0], item_order[j1], item_order[j2],
                                                                  item_order[j3], item_order[j4], item_order[i5]]
                                                            if item_num[0] + item_num[j1] + item_num[j2] + item_num[
                                                                j3] + \
                                                                    item_num[j4] + item_num[i5] <= 1000 and \
                                                                    area[0] + area[j1] + area[j2] + area[j3] + area[
                                                                j4] + area[i5] <= 250000000 and i5 != j1 and \
                                                                    i5 != j2 and i5 != j3 and i5 != j4:
                                                                u6 = waste(w6, df)
                                                                if u >= u6:
                                                                    # print('板材利用率：', u)
                                                                    break
                                                                else:
                                                                    w = w6
                                                                    j5 = i5
                                                                    u = u6
                                                                    # print('板材利用率：', u)

                                                                break

                                                    break
                                        break
                            break
                break
    elif len(item_order)==5:
        for i1 in range(1,len(item_order)):
            w2 = [item_order[0],item_order[i1]]
            if item_num[0]+item_num[i1]<=1000 and area[0]+area[i1]<=250000000:
                u2 = waste(w2,df)
                if u>=u2:
                    w = w1
                    u = u1
                    # print('板材利用率：', u)
                    break
                else:
                    w = w2
                    j1 = i1
                    u= u2
                    for i2 in range(1,len(item_order)):
                        w3 = [item_order[0], item_order[j1],item_order[i2]]
                        if item_num[0] + item_num[j1] +item_num[i2]<= 1000 and area[0] + area[j1] + area[i2]<= 250000000 and i2!=j1:
                            u3 = waste(w3,df)
                            if u>=u3:
                                # print('板材利用率：', u)
                                break
                            else:
                                w = w3
                                j2 = i2
                                u = u3
                                for i3 in range(1, len(item_order)):
                                    w4 = [item_order[0], item_order[j1], item_order[j2],item_order[i3]]
                                    if item_num[0] + item_num[j1] + item_num[j2] + item_num[i3]<= 1000 and area[0] + area[
                                        j1] + area[j2] + area [i3] <= 250000000 and i3 != j1 and i3!= j2:
                                        u4 = waste(w4, df)
                                        if u >= u4:
                                            # print('板材利用率：', u)
                                            break
                                        else:
                                            w = w4
                                            j3 = i3
                                            u = u4
                                            for i4 in range(1, len(item_order)):
                                                w5 = [item_order[0], item_order[j1], item_order[j2], item_order[j3],item_order[i4]]
                                                if item_num[0] + item_num[j1] + item_num[j2] + item_num[j3] +item_num[i4] <= 1000 and \
                                                        area[0] + area[j1] + area[j2] + area[j3] + area[i4]<= 250000000 and i4 != j1 and\
                                                        i4 != j2 and i4 != j3:
                                                    u5 = waste(w5, df)
                                                    if u >= u5:
                                                        # print('板材利用率：', u)
                                                        break
                                                    else:
                                                        w = w5
                                                        j4 = i4
                                                        u = u5
                                                        # print('板材利用率：', u)


                                                    break
                                        break
                            break
                break
    elif len(item_order) == 4:
        for i1 in range(1, len(item_order)):
            w2 = [item_order[0], item_order[i1]]
            if item_num[0] + item_num[i1] <= 1000 and area[0] + area[i1] <= 250000000:
                u2 = waste(w2, df)
                if u >= u2:
                    w = w1
                    u = u1
                    # print('板材利用率：', u)
                    break
                else:
                    w = w2
                    j1 = i1
                    u = u2
                    for i2 in range(1, len(item_order)):
                        w3 = [item_order[0], item_order[j1], item_order[i2]]
                        if item_num[0] + item_num[j1] + item_num[i2] <= 1000 and area[0] + area[j1] + area[
                            i2] <= 250000000 and i2 != j1:
                            u3 = waste(w3, df)
                            if u >= u3:
                                # print('板材利用率：', u)
                                break
                            else:
                                w = w3
                                j2 = i2
                                u = u3
                                for i3 in range(1, len(item_order)):
                                    w4 = [item_order[0], item_order[j1], item_order[j2], item_order[i3]]
                                    if item_num[0] + item_num[j1] + item_num[j2] + item_num[i3] <= 1000 and area[0] + \
                                            area[
                                                j1] + area[j2] + area[i3] <= 250000000 and i3 != j1 and i3 != j2:
                                        u4 = waste(w4, df)
                                        if u >= u4:
                                            # print('板材利用率：', u)
                                            break
                                        else:
                                            w = w4
                                            j3 = i3
                                            u = u4
                                            # print('板材利用率：', u)

                                        break
                            break
                break
    elif len(item_order) == 3:
        for i1 in range(1, len(item_order)):
            w2 = [item_order[0], item_order[i1]]
            if item_num[0] + item_num[i1] <= 1000 and area[0] + area[i1] <= 250000000:
                u2 = waste(w2, df)
                if u >= u2:
                    w = w1
                    u = u1
                    # print('板材利用率：', u)
                    break
                else:
                    w = w2
                    j1 = i1
                    u = u2
                    for i2 in range(1, len(item_order)):
                        w3 = [item_order[0], item_order[j1], item_order[i2]]
                        if item_num[0] + item_num[j1] + item_num[i2] <= 1000 and area[0] + area[j1] + area[
                            i2] <= 250000000 and i2 != j1:
                            u3 = waste(w3, df)
                            if u >= u3:
                                # print('板材利用率：', u)
                                break
                            else:
                                w = w3
                                j2 = i2
                                u = u3
                                # print('板材利用率：', u)

                            break
                break
    elif len(item_order) == 2:
        for i1 in range(1, len(item_order)):
            w2 = [item_order[0], item_order[i1]]
            if item_num[0] + item_num[i1] <= 1000 and area[0] + area[i1] <= 250000000:
                u2 = waste(w2, df)
                if u >= u2:
                    w = w1
                    u = u1
                    # print('板材利用率：', u)
                    break
                else:
                    w = w2
                    j1 = i1
                    u = u2
                    # print('板材利用率：', u)

                break
    elif len(item_order) == 1:
        w = w1
        u = u1
        # print('板材利用率：', u)
    return w
"""
将每个批次的item按材质分成子集合
"""
def exctitem(df):
    df_lister = []
    ls = df['item_material'].tolist()


    material_name = list(set(ls))
    material_name.sort(key=ls.index)

    for i in material_name:
        df1 = df.loc[df['item_material'] == i]
        df_lister.append(df1)
    return df_lister
"""
切割方案结果可视化，输出container.jpg文件
"""
def DrawContainers(df1,j,containerSize,id,draw_url):
    df = df1
    # Resize for image visibility
    n_col =7 #每一横排的原片图片数量
    scope = 0.1 # 缩放倍数
    # for i in range(len())
    id_list = []
    for i in range(len(j)):
        new_value = df1['原片序号'].tolist()[i] + j[i]
        id_list .append(new_value)
    df['原片序号'] = id_list

    n_max = max(df['原片序号'].tolist())
    item = list(zip(df['产品id'].tolist(), df['产品x坐标'].tolist(), df['产品y坐标'].tolist(),
                       df['产品x方向长度'].tolist(), df['产品y方向长度'].tolist(), df['原片序号'].tolist()))
    containerSize = tuple([scope  * x for x in containerSize])
    objects = tuple([(x[0], scope  * x[1], scope  * x[2], scope  * x[3], scope  * x[4], x[5]) for x in item])

    im = Image.new('RGB', (int(n_col * containerSize[0]), int((n_max//n_col+1) * containerSize[1])), (128, 128, 128))
    draw = ImageDraw.Draw(im)

    for i in range(n_max):
        row1 = i//n_col
        col1 = i%n_col

        draw.rectangle((containerSize[0]*col1, containerSize[1]*row1, containerSize[0]*col1 + containerSize[0], containerSize[1]*row1 + containerSize[1]),
                       fill='gray', outline='black')

    for obj in objects:
        text = 'id:'+str(obj[0])
        n = obj[5]-1
        row2 = n // n_col
        col2 = n % n_col
        draw.rectangle((containerSize[0]*col2+obj[1], containerSize[1]*row2+obj[2], containerSize[0]*col2 + obj[1] + obj[3], containerSize[1]*row2 + obj[2] + obj[4]),
                   fill='white', outline='red')
        draw.text((containerSize[0]*col2 + obj[1], containerSize[1]*row2 + obj[2] + obj[4] / 2), text, size=5, fill='black')

    im.save(draw_url+ str(id) + '.jpg', quality=60)
    # print('保存',id)
    return
def image_output(draw_url):
    draw_id = 0
    for i, j in draw:
        DrawContainers(i, j, containerSize,draw_id,draw_url)
        draw_id += 1
"""
主函数，配合solve()函数循环使用，输出各种数据
"""
def order_arrage(df,item_order,item_num,area):
    df_solve = df

    df_ls = []
    ind=0
    ind_ls = []
    for i in range(len(item_order)):
        if len(item_order) >0:
            pick = solve(df_solve)
            df_pick = output(pick,df_solve)
            df_ls.append(df_pick)
            ind += 1
            ind_ls.append(ind)
            df_pick.insert(df_pick.shape[1], '订单批次', ind)
            item_order,item_num,area = remove(pick,item_order,item_num,area)
            df_solve = output(item_order, df_solve)#从订单池中删除以排布的订单

            # print('*************剩余订单****************', len(item_order),'批次数量:', ind)
    B2_record_ls = []
    useeff_ls = []
    container_num_t = 0
    spaceused_t = 0
    container_draw_ls = []
    B2_record_draw_ls = []
    for j in df_ls:
        container_num = 0
        spaceused = 0
        container_draw = []
        B2_record_draw = []
        containeruse_draw = 0
        record_ls = exctitem(j)
        for i in record_ls:
            objects = read(i)
            B2_record, containerused, space = record(objects)
            for i in range(len(B2_record)):
                container_draw.append(containeruse_draw)

            B2_record_ls.append(B2_record)
            B2_record_draw.append(B2_record)
            containeruse_draw += containerused
            container_num += containerused
            spaceused += space

        draw_add = pd.concat(B2_record_draw)
        B2_record_draw_ls.append(draw_add)
        container_draw_ls.append((container_draw))
        container_num_t += container_num
        spaceused_t += spaceused
        useeff = spaceused / (container_num * containerSize[0] * containerSize[1])
        useeff_ls.append(useeff)
    B2_record_df = pd.concat(B2_record_ls)
    useeff_df = pd.DataFrame(useeff_ls)

    print('总板材利用率', spaceused_t / (container_num_t * containerSize[0] * containerSize[1]))
    print('板材总量', container_num_t)
    print('批次数量：', len(df_ls))
    return B2_record_df,useeff_df,zip(B2_record_draw_ls,container_draw_ls)
"""
主函数
"""
input_url = './子问题2-数据集B/dataB5.csv'#输入数据集路径
csv_name = './output/sum_order5.csv'#输出订单排布表格
draw_url = './output/B5_fig/B5_'#图片保存路径（/文件夹/图片名统一前缀）
# uff_name ='useeff1.csv'
containerSize = (2440, 1220)
url = input_url
df = add_area(url)
item_order,item_num,area = order_record(df)
B2_record_df,useeff_df,draw= order_arrage(df,item_order,item_num,area)
B2_record_df.to_csv(csv_name, index=False) #输出订单排布表格
image_output(draw_url)
# useeff_df.to_csv(uff_name, index=False)











