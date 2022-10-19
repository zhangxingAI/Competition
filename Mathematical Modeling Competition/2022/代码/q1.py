import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from PIL import Image, ImageDraw
import os
"""
读取原数据，对原数据以长宽比进行排序，输出item信息（长，宽，id号），并输出原片材质（问题一中材质统一）
"""
def read(df):
    df1 =df
    ls = []
    xls=[]
    yls=[]
    for i, j in zip(df1['item_length'].tolist(), df1['item_width'].tolist()):
        k = min(i, j) / max(i, j)
        ls.append(k)
    df1['尺寸'] = ls
    df2 = df1.sort_values(by=['尺寸'],ascending = False)
    # print(df)
    for i, j in zip(df2['item_length'].tolist(), df2['item_width'].tolist()):
        x = max(i, j)
        y = min(i, j)
        xls.append(x)
        yls.append(y)
    result = zip(xls, yls, df2['item_id'])

    # result = zip(df['item_length'].tolist(),df['item_width'].tolist(),df['item_id'])
    item_material = df2['item_material'].tolist()[0]
    return list(result),item_material
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
                item_material.append(item_material_name)
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
                item_material.append(item_material_name)
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
            item_material.append(item_material_name)


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
            item_material.append(item_material_name)

        elif obj[0] <= widthLeft and obj[1] <= heightLeft:
            widthLeft -= obj[0]
            rowHeight = max(rowHeight, obj[1])
            X.append(containerSize[0] - widthLeft - obj[0])
            Y.append(rowHeight_record)
            x.append(obj[0])
            y.append(obj[1])
            container_id.append(containersUsed)
            item_id.append(obj[2])
            item_material.append(item_material_name)

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
            item_material.append(item_material_name)

        elif obj[1] <= widthLeft and obj[0] > widthLeft and obj[0] <= heightLeft and obj[1] > (heightLeft-rowHeight):
            widthLeft -= obj[1]
            rowHeight = max(rowHeight, obj[0])
            X.append(containerSize[0] - widthLeft - obj[1])
            Y.append(rowHeight_record)
            x.append(obj[1])
            y.append(obj[0])
            container_id.append(containersUsed)
            item_id.append(obj[2])
            item_material.append(item_material_name)

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
            item_material.append(item_material_name)
    # 输出方案
    df = pd.DataFrame(list(zip(item_material, container_id, item_id, X, Y, x, y)),
                      columns=['原片材质', '原片序号', '产品id', '产品x坐标', '产品y坐标', '产品x方向长度', '产品y方向长度'])
    containersUsed = max(df['原片序号'].tolist())
    efficiency = usage(containerSize[0], containerSize[1], containersUsed, objects)
    print("原片总数: ", containersUsed)
    print("板材利用率: ", efficiency)
    print(df)
    # df3 = df['产品id']
    # print(df3.duplicated().sum())
    return df
"""
切割方案结果可视化，输出container.jpg文件
"""
def DrawContainers(df,containerSize,url_draw):
    # Resize for image visibility
    n_col =7 #每一横排的原片图片数量
    scope = 0.1 # 缩放倍数
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

    im.save(url_draw, quality=100)
    return

url = './子问题1-数据集A/dataA4.csv'#输入数据集路径
df = pd.read_csv(url, engine='python', on_bad_lines='skip')
containerSize = (2440, 1220)
objects,item_material_name = read(df)
record = record(objects)
record.to_csv('./output/cut_program4.csv', index=False)#输出csv文件
url_draw = './output/A4.jpg'#图片保存路径（/文件夹/图片名）
DrawContainers(record, containerSize,url_draw)





