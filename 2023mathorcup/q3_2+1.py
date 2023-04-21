import numpy as np
import pandas as pd

interest_rate = 0.08

def final_income_2(t1, h1, t2, h2):
    total_pass_rate = t1 * t2
    total_bad_rate = (h1 + h2) / 2
    return interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_rate

def final_income_3(t1, h1, t2, h2, t3, h3):
    total_pass_rate = t1 * t2 * t3
    total_bad_rate = (h1 + h2 + h3) / 3
    return interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_rate

# 读取数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values

# 初始化最大收入值和对应的信用评分卡和阈值
max_income_2 = float('-inf')
first_card, second_card, first_threshold, second_threshold = None, None, None, None

# 遍历所有信用评分卡和阈值的组合，找到最大收入的组合
for card1 in range(100):
    for threshold1 in range(10):
        t1, h1 = data[threshold1, 2 * card1], data[threshold1, 2 * card1 + 1]
        for card2 in range(card1 + 1, 100):
            for threshold2 in range(10):
                t2, h2 = data[threshold2, 2 * card2], data[threshold2, 2 * card2 + 1]
                income = final_income_2(t1, h1, t2, h2)
                if income > max_income_2:
                    max_income_2 = income
                    first_card, second_card, first_threshold, second_threshold = card1, card2, threshold1, threshold2

# 计算总通过率和总坏账率
total_pass_rate = data[first_threshold, 2 * first_card] * data[second_threshold, 2 * second_card]
total_bad_rate = (data[first_threshold, 2 * first_card + 1] + data[second_threshold, 2 * second_card + 1]) / 2

# 初始化第三次选择的最大收入值和对应的信用评分卡和阈值
max_income_3 = float('-inf')
third_card, third_threshold = None, None

# 从剩余的信用评分卡中选择第三个信用评分卡和阈值，使得最终收入最大
for card in range(100):
    if card == first_card or card == second_card:
        continue
    for threshold in range(10):
        t3, h3 = data[threshold, 2 * card], data[threshold, 2 * card + 1]
        income = final_income_3(total_pass_rate, total_bad_rate*2, t3, h3, 1, 0)
        if income > max_income_3:
            max_income_3 = income
            third_card, third_threshold = card, threshold

# 输出结果
print("从信用评分卡：{} 中选择阈值：{}，通过率：{}，坏账率：{}".format(first_card + 1, first_threshold + 1, data[first_threshold, 2 * first_card], data[first_threshold, 2 * first_card + 1]))
print("从信用评分卡：{} 中选择阈值：{}，通过率：{}，坏账率：{}".format(second_card + 1, second_threshold + 1, data[second_threshold, 2 * second_card], data[second_threshold, 2 * second_card + 1]))
print("从信用评分卡：{} 中选择阈值：{}，通过率：{}，坏账率：{}".format(third_card + 1, third_threshold + 1, data[third_threshold, 2 * third_card], data[third_threshold, 2 * third_card + 1]))

print("总通过率:", total_pass_rate * data[third_threshold, 2 * third_card])
print("总坏账率:", (total_bad_rate*2 + data[third_threshold, 2 * third_card + 1]) / 3)

# 计算最终收入
final_income_value = final_income_3(data[first_threshold, 2 * first_card], data[first_threshold, 2 * first_card + 1],
                                  data[second_threshold, 2 * second_card], data[second_threshold, 2 * second_card + 1],
                                  data[third_threshold, 2 * third_card], data[third_threshold, 2 * third_card + 1])
print("最终收入:", final_income_value)



